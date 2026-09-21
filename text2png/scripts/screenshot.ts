import puppeteer from "puppeteer-core";
import type { Page } from "puppeteer-core";
import path from "node:path";
import process from "node:process";
import { statSync } from "node:fs";
import { mkdir } from "node:fs/promises";
import { execSync } from "node:child_process";

type CliArgs = {
  html: string | null;
  out: string | null;
  bg: string;
  width: number;
  padding: number;
  dpr: number;
  format: "png" | "webp";
  help: boolean;
};

function printUsage(): void {
  console.log(`Usage:
  npx -y bun screenshot.ts --html <file> --out <file> [options]

Options:
  --html <path>       Input HTML file path (required)
  --out <path>        Output image file path (required)
  --bg <color>        Background color for padding area (default: #ffffff)
  --width <px>        Viewport width in pixels (default: 860)
  --padding <px>      Padding around content (default: 32)
  --dpr <1-4>         Device pixel ratio (default: 4)
  --format <type>     Output format: png or webp (default: png)
  -h, --help          Show help`);
}

function parseArgs(argv: string[]): CliArgs {
  const out: CliArgs = {
    html: null,
    out: null,
    bg: "#ffffff",
    width: 860,
    padding: 32,
    dpr: 4,
    format: "png",
    help: false,
  };

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]!;
    if (a === "--help" || a === "-h") { out.help = true; continue; }
    if (a === "--html") { out.html = argv[++i] || null; continue; }
    if (a === "--out") { out.out = argv[++i] || null; continue; }
    if (a === "--bg") { out.bg = argv[++i] || "#ffffff"; continue; }
    if (a === "--width") { out.width = parseInt(argv[++i] || "860", 10); continue; }
    if (a === "--padding") { out.padding = parseInt(argv[++i] || "32", 10); continue; }
    if (a === "--dpr") { out.dpr = Math.min(4, Math.max(1, parseInt(argv[++i] || "4", 10))); continue; }
    if (a === "--format") {
      const fmt = (argv[++i] || "png").toLowerCase();
      out.format = fmt === "webp" ? "webp" : "png";
      continue;
    }
    if (a.startsWith("-")) throw new Error(`Unknown option: ${a}`);
  }
  return out;
}

/** Find system Chrome executable */
function findChrome(): string {
  const candidates =
    process.platform === "win32"
      ? [
          process.env["PROGRAMFILES"] + "\\Google\\Chrome\\Application\\chrome.exe",
          process.env["PROGRAMFILES(X86)"] + "\\Google\\Chrome\\Application\\chrome.exe",
          process.env["LOCALAPPDATA"] + "\\Google\\Chrome\\Application\\chrome.exe",
        ]
      : process.platform === "darwin"
        ? [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
          ]
        : [
            "google-chrome",
            "google-chrome-stable",
            "chromium-browser",
            "chromium",
          ];

  for (const cmd of candidates) {
    try {
      if (process.platform === "win32") {
        statSync(cmd);
        return cmd;
      } else {
        const fullPath = execSync(`which "${cmd}" 2>/dev/null`, { stdio: "pipe" })
          .toString()
          .trim();
        if (fullPath) return fullPath;
      }
    } catch {
      // not found, try next
    }
  }

  throw new Error(
    "Chrome not found. Please install Google Chrome.\n" +
    "  https://www.google.com/chrome/"
  );
}

async function launchBrowser(chromePath: string, retries = 1) {
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await puppeteer.launch({
        executablePath: chromePath,
        headless: true,
        args: ["--no-sandbox", "--disable-setuid-sandbox"],
      });
    } catch (e) {
      if (attempt === retries) throw e;
      console.error(`[warn] Chrome launch failed, retrying...`);
      await new Promise((r) => setTimeout(r, 500));
    }
  }
  throw new Error("Unreachable");
}

/** 测量 .wrap（或 body）的盒子 */
async function measureBox(page: Page) {
  return await page.evaluate(() => {
    const el = (document.querySelector(".wrap") || document.body) as HTMLElement;
    const r = el.getBoundingClientRect();
    return { x: r.x, y: r.y, width: r.width, height: r.height };
  });
}

/** 等尺寸稳定：连续两帧一致就返回，超时也返回（避免字体/图片慢时卡死） */
async function waitForStableSize(page: Page, timeoutMs = 3000): Promise<void> {
  await page.evaluate(
    (timeout: number) =>
      new Promise<void>((resolve) => {
        let last = "";
        let stable = 0;
        const started = Date.now();
        const tick = () => {
          const el = (document.querySelector(".wrap") || document.body) as HTMLElement;
          const r = el.getBoundingClientRect();
          const key = `${Math.round(r.width)}x${Math.round(r.height)}`;
          stable = key === last ? stable + 1 : 0;
          last = key;
          if (stable >= 2 || Date.now() - started > timeout) return resolve();
          requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      }),
    timeoutMs,
  );
}

async function screenshot(args: CliArgs): Promise<void> {
  const htmlPath = path.resolve(args.html!);
  const outPath = path.resolve(args.out!);
  const pad = args.padding;

  await mkdir(path.dirname(outPath), { recursive: true });

  const chromePath = findChrome();
  console.error(`[info] using Chrome: ${chromePath}`);

  const browser = await launchBrowser(chromePath);

  try {
    const page = await browser.newPage();

    // Phase 1: 用高视口渲染，测量内容尺寸
    await page.setViewport({ width: args.width, height: 4000, deviceScaleFactor: args.dpr });
    // 用 domcontentloaded：外链字体/图片慢时不会像 networkidle0 那样拖到超时
    await page.goto(`file://${htmlPath}`, { waitUntil: "domcontentloaded" });

    // 字体最多等 5s；远程字体不可达时直接继续（用回退字体渲染）
    await Promise.race([
      page.evaluate(() => document.fonts.ready),
      new Promise((r) => setTimeout(r, 5000)),
    ]);
    await waitForStableSize(page);

    // 先铺背景色，它会参与测量结果
    await page.evaluate((bg: string) => {
      document.documentElement.style.backgroundColor = bg;
    }, args.bg);

    // Phase 2: 测量 → 调视口 → 复测；尺寸变了就再来一轮（最多 3 轮）
    let clip = { x: 0, y: 0, width: args.width, height: 400 };
    for (let pass = 0; pass < 3; pass++) {
      const box = await measureBox(page);
      clip = {
        x: Math.max(0, box.x - pad),
        y: Math.max(0, box.y - pad),
        width: box.width + pad * 2,
        height: box.height + pad * 2,
      };
      const viewportH = Math.ceil(clip.y + clip.height + 10);
      await page.setViewport({ width: args.width, height: viewportH, deviceScaleFactor: args.dpr });
      await waitForStableSize(page, 1500);
      const after = await measureBox(page);
      if (Math.abs(after.height - box.height) <= 1 && Math.abs(after.width - box.width) <= 1) break;
      if (pass === 2) console.error("[warn] 调整视口后内容尺寸仍变化，按最后一轮结果截图");
    }

    await page.screenshot({
      path: outPath,
      type: args.format,
      ...(args.format === "webp" ? { quality: 92 } : {}),
      clip,
    });

    console.log(outPath);
  } finally {
    await browser.close();
  }
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) { printUsage(); return; }
  if (!args.html) { console.error("Error: --html is required"); printUsage(); process.exitCode = 1; return; }
  if (!args.out) { console.error("Error: --out is required"); printUsage(); process.exitCode = 1; return; }

  await screenshot(args);
}

main().catch((e) => {
  console.error(e instanceof Error ? e.message : String(e));
  process.exit(1);
});
