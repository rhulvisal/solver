import random
from typing import Dict, Tuple, Optional


class BrowserConfig:

    SEC_CH_UA_CONFIGS = {
        "chrome": {
            "139": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "138": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "137": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "136": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"'
        },
        "edge": {
            "139": '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
            "138": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            "137": '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"'
        },
        "avast": {
            "138": '"Not)A;Brand";v="8", "Chromium";v="138", "Avast Secure Browser";v="138"',
            "137": '"Avast Secure Browser";v="137", "Chromium";v="137", "Not/A)Brand";v="24"'
        },
        "brave": {
            "139": '"Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"',
            "138": '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"',
            "137": '"Brave";v="137", "Chromium";v="137", "Not/A)Brand";v="24"'
        }
    }

    USER_AGENT_CONFIGS = {
        "chrome": {
            "139": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "138": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "137": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "136": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        },
        "edge": {
            "139": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
            "138": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "137": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
        },
        "avast": {
            "138": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Avast/138.0.0.0",
            "137": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Avast/137.0.0.0"
        },
        "brave": {
            "139": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "138": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "137": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        }
    }

    def __init__(self):
        self.available_browsers = list(self.USER_AGENT_CONFIGS.keys())

    def get_random_browser_config(self, browser_type=None) -> Tuple[str, str, str, str]:
        # FIXED: Map requested browser to available config, dont randomly pick uninstalled browsers
        browser_map = {
            'chromium': 'chrome',
            'chrome': 'chrome',
            'msedge': 'edge',
            'edge': 'edge',
            'brave': 'brave',
            'avast': 'avast'
        }

        if browser_type in browser_map:
            browser = browser_map[browser_type]
        else:
            browser = random.choice(self.available_browsers)

        versions = list(self.USER_AGENT_CONFIGS[browser].keys())
        version = random.choice(versions)
        user_agent = self.USER_AGENT_CONFIGS[browser][version]
        sec_ch_ua = self.SEC_CH_UA_CONFIGS.get(browser, {}).get(version, "")
        return browser, version, user_agent, sec_ch_ua

    def get_browser_config(self, browser: str, version: str) -> Optional[Tuple[str, str]]:
        try:
            user_agent = self.USER_AGENT_CONFIGS[browser][version]
            sec_ch_ua = self.SEC_CH_UA_CONFIGS.get(browser, {}).get(version, "")
            return user_agent, sec_ch_ua
        except KeyError:
            return None


browser_config = BrowserConfig()

import aiosqlite
import json
import logging
from typing import Dict, Any, Optional, Union

DB_PATH = "try.db"
PRAGMA_SETTINGS = [
    "PRAGMA journal_mode=WAL",
    "PRAGMA synchronous=NORMAL",
    "PRAGMA cache_size=10000",
    "PRAGMA temp_store=MEMORY",
    "PRAGMA busy_timeout=30000"
]

_db: Optional[aiosqlite.Connection] = None


async def init_db():
    global _db
    try:
        _db = await aiosqlite.connect(DB_PATH)
        for pragma in PRAGMA_SETTINGS:
            await _db.execute(pragma)
        await _db.execute("""
            CREATE TABLE IF NOT EXISTS results (
                task_id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await _db.commit()
        logging.getLogger("TurnstileAPIServer").info(f"Database initialized in WAL mode: {DB_PATH}")
    except Exception as e:
        logging.getLogger("TurnstileAPIServer").error(f"Database initialization error: {e}")
        raise


async def save_result(task_id: str, task_type: str, data: Union[Dict[str, Any], str]) -> None:
    try:
        data_json = json.dumps(data) if isinstance(data, dict) else data
        await _db.execute(
            "REPLACE INTO results (task_id, type, data) VALUES (?, ?, ?)",
            (task_id, task_type, data_json)
        )
        await _db.commit()
    except Exception as e:
        logging.getLogger("TurnstileAPIServer").error(f"Error saving result {task_id}: {e}")
        raise


async def load_result(task_id: str) -> Optional[Union[Dict[str, Any], str]]:
    try:
        async with _db.execute("SELECT data FROM results WHERE task_id = ?", (task_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except json.JSONDecodeError:
                    return row[0]
        return None
    except Exception as e:
        logging.getLogger("TurnstileAPIServer").error(f"Error loading result {task_id}: {e}")
        return None


import os
import sys
import time
import uuid
import logging
import asyncio
import subprocess
from typing import Optional, Union
from quart import Quart, request, jsonify
from patchright.async_api import async_playwright
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box


COLORS = {
    'MAGENTA': '[35m',
    'BLUE': '[34m',
    'GREEN': '[32m',
    'YELLOW': '[33m',
    'RED': '[31m',
    'RESET': '[0m',
}

DEFAULT_CONTEXT_MAX_USES = 3  # REDUCED from 25 to prevent fingerprint accumulation


class CustomLogger(logging.Logger):
    @staticmethod
    def format_message(level, color, message):
        timestamp = time.strftime('%H:%M:%S')
        return f"[{timestamp}] [{COLORS.get(color)}{level}{COLORS.get('RESET')}] -> {message}"

    def debug(self, message, *args, **kwargs):
        super().debug(self.format_message('DEBUG', 'MAGENTA', message), *args, **kwargs)

    def info(self, message, *args, **kwargs):
        super().info(self.format_message('INFO', 'BLUE', message), *args, **kwargs)

    def success(self, message, *args, **kwargs):
        super().info(self.format_message('SUCCESS', 'GREEN', message), *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        super().warning(self.format_message('WARNING', 'YELLOW', message), *args, **kwargs)

    def error(self, message, *args, **kwargs):
        super().error(self.format_message('ERROR', 'RED', message), *args, **kwargs)


logging.setLoggerClass(CustomLogger)
logger = logging.getLogger("TurnstileAPIServer")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


class TurnstileAPIServer:

    def __init__(self, headless: bool, useragent: Optional[str], debug: bool, browser_type: str, thread: int, proxy_support: bool, context_max_uses: int = DEFAULT_CONTEXT_MAX_USES):
        self.app = Quart(__name__)
        self.debug = debug
        self.browser_type = browser_type
        self.headless = headless
        self.thread_count = thread
        self.proxy_support = proxy_support
        self.context_max_uses = max(1, context_max_uses)
        self.browser_pool = asyncio.Queue()
        self.context_pool = asyncio.Queue()
        self.console = Console()

        self.useragent = useragent
        self.sec_ch_ua = None

        if self.browser_type in ['chromium', 'chrome', 'msedge', 'brave', 'avast'] and not useragent:
            browser, version, useragent, sec_ch_ua = browser_config.get_random_browser_config(self.browser_type)
            self.browser_name = browser
            self.browser_version = version
            self.useragent = useragent
            self.sec_ch_ua = sec_ch_ua
        else:
            self.browser_name = 'custom'
            self.browser_version = 'custom'

        # Caches populated at startup
        self._turnstile_js_cache: Optional[str] = None
        self._proxy_list: list = []

        self._setup_routes()

    def _load_caches(self):
        try:
            with open('turnstile_api.js', 'r') as f:
                self._turnstile_js_cache = f.read()
            if self.debug:
                logger.debug(f"Turnstile JS cache loaded: {len(self._turnstile_js_cache)} chars")
        except Exception as e:
            self._turnstile_js_cache = None
            logger.error(f"CRITICAL: turnstile_api.js not found or unreadable: {e}")

        if self.proxy_support:
            proxy_path = os.path.join(os.getcwd(), "proxies.txt")
            try:
                with open(proxy_path) as f:
                    self._proxy_list = [line.strip() for line in f if line.strip()]
                if self.debug:
                    logger.debug(f"Loaded {len(self._proxy_list)} proxies")
            except FileNotFoundError:
                logger.warning(f"Proxy file not found: {proxy_path}")
            except Exception as e:
                logger.error(f"Error reading proxy file: {str(e)}")

    def display_welcome(self):
        self.console.clear()

        combined_text = Text()
        combined_text.append("
 GitHub: ", style="bold white")
        combined_text.append("https://github.com/rythampkhandelwal", style="cyan")
        combined_text.append("
 Version: ", style="bold white")
        combined_text.append("1.3b-railway", style="green")
        combined_text.append("
")

        info_panel = Panel(
            Align.left(combined_text),
            title="[bold blue]Turnstile Solver[/bold blue]",
            subtitle="[bold magenta]Dev by Rytham Khandelwal[/bold magenta]",
            box=box.ROUNDED,
            border_style="bright_blue",
            padding=(0, 1),
            width=50
        )

        self.console.print(info_panel)
        self.console.print()

    def _setup_routes(self) -> None:
        self.app.before_serving(self._startup)
        self.app.route('/turnstile', methods=['GET'])(self.process_turnstile)
        self.app.route('/result', methods=['GET'])(self.get_result)
        self.app.route('/')(self.index)

    async def _startup(self) -> None:
        self.display_welcome()
        logger.info("Starting browser initialization")

        # RAILWAY DIAGNOSTIC: Check what browsers are actually installed
        try:
            result = subprocess.run(["which", "chromium"], capture_output=True, text=True)
            logger.info(f"Chromium binary: {result.stdout.strip() or 'NOT FOUND'}")
            result = subprocess.run(["chromium", "--version"], capture_output=True, text=True)
            logger.info(f"Chromium version: {result.stdout.strip() or 'NOT FOUND'}")
        except Exception as e:
            logger.warning(f"Could not check chromium binary: {e}")

        try:
            await init_db()
            self._load_caches()
            await self._initialize_browser()
        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            raise

    async def _launch_single_browser(self, playwright, index: int, config: dict):
        browser_args = [
            f"--user-agent={config['useragent']}",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-site-isolation-trials",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-accelerated-2d-canvas",
            "--disable-gpu",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-breakpad",
            "--disable-component-extensions-with-background-pages",
            "--disable-extensions",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--disable-renderer-backgrounding",
            "--force-color-profile=srgb",
            "--metrics-recording-only",
            "--safebrowsing-disable-auto-update",
            "--disable-webgl",
            "--disable-3d-apis",
            "--disable-canvas-aa",
            "--disable-software-rasterizer",
        ]

        # FIXED: Use patchright's chromium directly, dont use channel (which expects system browser)
        browser = await playwright.chromium.launch(
            headless=self.headless,
            args=browser_args
        )

        for _ in range(2):
            context, page = await self._create_context_and_page(browser, config)
            await self.context_pool.put((index, browser, context, page, config, 0))

        await self.browser_pool.put((index, browser, config))

        if self.debug:
            logger.info(f"Browser {index} initialized successfully with {config['browser_name']} {config['browser_version']}")

    async def _initialize_browser(self) -> None:
        playwright = await async_playwright().start()

        config = {
            'browser_name': self.browser_name,
            'browser_version': self.browser_version,
            'useragent': self.useragent,
            'sec_ch_ua': self.sec_ch_ua or '',
        }

        await asyncio.gather(*(
            self._launch_single_browser(playwright, i + 1, config)
            for i in range(self.thread_count)
        ))

        logger.info(f"Browser pool initialized with {self.browser_pool.qsize()} browsers")
        logger.info(f"All browsers using configuration: {self.browser_name} {self.browser_version}")

        if self.debug:
            logger.debug(f"User-Agent: {config['useragent']}")
            logger.debug(f"Sec-CH-UA: {config['sec_ch_ua']}")

    async def _create_context_and_page(self, browser, config: dict, proxy: Optional[str] = None):
        context_options = {
            "user_agent": config['useragent'],
            "viewport": {"width": 1366, "height": 768},
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "permissions": [],
            "geolocation": None,
        }
        if config.get('sec_ch_ua', '').strip():
            context_options['extra_http_headers'] = {'sec-ch-ua': config['sec_ch_ua']}

        if proxy:
            parts = proxy.split(':')
            if len(parts) == 5:
                proxy_scheme, proxy_ip, proxy_port, proxy_user, proxy_pass = parts
                context_options["proxy"] = {
                    "server": f"{proxy_scheme}://{proxy_ip}:{proxy_port}",
                    "username": proxy_user,
                    "password": proxy_pass
                }
            elif len(parts) == 4:
                proxy_host, proxy_port, proxy_user, proxy_pass = parts
                context_options["proxy"] = {
                    "server": f"http://{proxy_host}:{proxy_port}",
                    "username": proxy_user,
                    "password": proxy_pass
                }
            elif len(parts) == 2:
                context_options["proxy"] = {"server": f"http://{parts[0]}:{parts[1]}"}
            elif '://' in proxy:
                try:
                    scheme_part, auth_part = proxy.split('://')
                    auth, address = auth_part.split('@', 1)
                    username, password = auth.split(':', 1)
                    ip, port = address.split(':')
                    context_options["proxy"] = {
                        "server": f"{scheme_part}://{ip}:{port}",
                        "username": username,
                        "password": password
                    }
                except ValueError:
                    raise ValueError(f"Invalid proxy format: {proxy}")
            else:
                raise ValueError(f"Invalid proxy format: {proxy}")

        context = await browser.new_context(**context_options)
        await context.grant_permissions([], origin=None)
        page = await context.new_page()
        return context, page

    def _make_solve_handler(self, target_url: str):
        normalized = target_url.rstrip('/')
        js_cache = self._turnstile_js_cache

        async def handler(route):
            url = route.request.url
            resource_type = route.request.resource_type

            if resource_type == 'document' and url.rstrip('/') == normalized:
                await route.fulfill(
                    status=200,
                    content_type='text/html',
                    body='<!DOCTYPE html><html><head></head><body></body></html>'
                )
                return

            if 'challenges.cloudflare.com/turnstile/v0/api.js' in url and js_cache:
                await route.fulfill(status=200, content_type='application/javascript', body=js_cache)
                return

            if resource_type in ('document', 'script', 'xhr', 'fetch') or 'cloudflare.com' in url:
                await route.continue_()
            else:
                await route.abort()

        return handler

    async def _clear_page_state(self, page):
        try:
            await page.evaluate("""
                () => {
                    try { localStorage.clear(); } catch(e) {}
                    try { sessionStorage.clear(); } catch(e) {}
                    try {
                        document.cookie.split(';').forEach(c => {
                            const [name] = c.split('=');
                            if (name) {
                                document.cookie = name.trim() + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=' + window.location.hostname;
                                document.cookie = name.trim() + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;';
                            }
                        });
                    } catch(e) {}
                    document.querySelectorAll('iframe').forEach(f => {
                        try { f.remove(); } catch(e) {}
                    });
                    const existing = document.getElementById('captcha-overlay');
                    if (existing) {
                        try { existing.remove(); } catch(e) {}
                    }
                    try {
                        if (window.indexedDB && window.indexedDB.databases) {
                            window.indexedDB.databases().then(dbs => {
                                dbs.forEach(db => {
                                    try { window.indexedDB.deleteDatabase(db.name); } catch(e) {}
                                });
                            });
                        }
                    } catch(e) {}
                }
            """)
        except Exception as e:
            if self.debug:
                logger.debug(f"State clearing warning (non-critical): {e}")

        try:
            await page.context.clear_cookies()
        except Exception:
            pass

    async def _click_turnstile_via_cdp(self, page, index: int, wait_ms: int = 3000):
        try:
            iframe_el = page.locator('iframe[src*="challenges.cloudflare.com"]').first
            await iframe_el.wait_for(state='visible', timeout=wait_ms)
            await asyncio.sleep(random.uniform(0.1, 0.4))
            await iframe_el.click(force=True, timeout=1000)
            return True
        except Exception:
            pass
        return False

    async def _load_captcha_overlay(self, page, websiteKey: str, action: str = '', index: int = 0):
        script = f"""
        const existing = document.querySelector('#captcha-overlay');
        if (existing) existing.remove();

        const overlay = document.createElement('div');
        overlay.id = 'captcha-overlay';
        overlay.style.position = 'absolute';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100vw';
        overlay.style.height = '100vh';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        overlay.style.display = 'block';
        overlay.style.justifyContent = 'center';
        overlay.style.alignItems = 'center';
        overlay.style.zIndex = '1000';

        const captchaDiv = document.createElement('div');
        captchaDiv.className = 'cf-turnstile';
        captchaDiv.setAttribute('data-sitekey', '{websiteKey}');
        captchaDiv.setAttribute('data-callback', 'onCaptchaSuccess');
        captchaDiv.setAttribute('data-action', '{action}');

        overlay.appendChild(captchaDiv);
        document.body.appendChild(overlay);

        const script = document.createElement('script');
        script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js';
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
        """

        await page.evaluate(script)
        if self.debug:
            logger.debug(f"Browser {index}: Created CAPTCHA overlay with sitekey: {websiteKey}")

    async def _wait_for_token(self, page, timeout: int = 2000) -> Optional[str]:
        try:
            await page.wait_for_function(
                "() => Array.from(document.querySelectorAll('input[name=\"cf-turnstile-response\"]')).some(el => el.value)",
                timeout=timeout,
                polling=50
            )
            return await page.evaluate(
                "() => Array.from(document.querySelectorAll('input[name=\"cf-turnstile-response\"]')).map(el => el.value).find(v => v) || null"
            )
        except Exception:
            return None

    async def _solve_turnstile(self, task_id: str, url: str, sitekey: str, action: Optional[str] = None, cdata: Optional[str] = None):
        proxy = None
        context_uses = 0
        token = None
        start_time = time.time()

        if not self.proxy_support and not self.context_pool.empty():
            index, browser, context, page, config, context_uses = await self.context_pool.get()
            if self.debug:
                logger.debug(f"Browser {index}: Using warm page from pool (use {context_uses}/{self.context_max_uses})")
        else:
            index, browser, config = await self.browser_pool.get()
            context = None
            page = None

            if self.proxy_support:
                proxy = random.choice(self._proxy_list) if self._proxy_list else None
                if self.debug:
                    logger.debug(f"Browser {index}: Selected proxy: {proxy}" if proxy else f"Browser {index}: No proxies available")

            context, page = await self._create_context_and_page(browser, config, proxy=proxy)

        try:
            if hasattr(browser, 'is_connected') and not browser.is_connected():
                if self.debug:
                    logger.warning(f"Browser {index}: Browser disconnected, skipping")
                if not self.proxy_support:
                    await self.context_pool.put((index, browser, context, page, config, context_uses))
                else:
                    await self.browser_pool.put((index, browser, config))
                await save_result(task_id, "turnstile", {"value": "CAPTCHA_FAIL", "elapsed_time": 0})
                return
        except Exception as e:
            if self.debug:
                logger.warning(f"Browser {index}: Cannot check browser state: {str(e)}")

        route_handler = None
        solve_failed = False

        try:
            if self.debug:
                logger.debug(f"Browser {index}: Starting Turnstile solve for URL: {url} with Sitekey: {sitekey} | Action: {action} | Cdata: {cdata} | Proxy: {proxy}")

            target_url = url if url.startswith(("http://", "https://")) else f"https://{url}"

            await self._clear_page_state(page)
            await asyncio.sleep(random.uniform(0.05, 0.25))

            route_handler = self._make_solve_handler(target_url)
            await page.route("**/*", route_handler)

            await page.goto(target_url, wait_until='commit', timeout=10000)

            await self._load_captcha_overlay(page, sitekey, action or '', index)

            token = await self._wait_for_token(page, timeout=400)

            if not token:
                for attempt in range(3):
                    iframe_wait = 3000 if attempt == 0 else 400
                    token_wait = 3000 if attempt == 0 else 2000

                    clicked = await self._click_turnstile_via_cdp(page, index, wait_ms=iframe_wait)
                    if clicked and self.debug:
                        logger.debug(f"Browser {index}: Clicked iframe on attempt {attempt + 1}")

                    token = await self._wait_for_token(page, timeout=token_wait)
                    if token:
                        break
                    if self.debug:
                        logger.debug(f"Browser {index}: Click attempt {attempt + 1} didn't produce token, retrying")

            if token:
                elapsed_time = round(time.time() - start_time, 3)
                logger.success(f"Browser {index}: Successfully solved captcha - {COLORS['MAGENTA']}{token[:10]}{COLORS['RESET']} in {COLORS['GREEN']}{elapsed_time}{COLORS['RESET']} Seconds")
                await save_result(task_id, "turnstile", {"value": token, "elapsed_time": elapsed_time})
                return

            solve_failed = True
            elapsed_time = round(time.time() - start_time, 3)
            await save_result(task_id, "turnstile", {"value": "CAPTCHA_FAIL", "elapsed_time": elapsed_time})
            if self.debug:
                logger.error(f"Browser {index}: Error solving Turnstile in {COLORS['RED']}{elapsed_time}{COLORS['RESET']} Seconds")

        except Exception as e:
            solve_failed = True
            elapsed_time = round(time.time() - start_time, 3)
            await save_result(task_id, "turnstile", {"value": "CAPTCHA_FAIL", "elapsed_time": elapsed_time})
            if self.debug:
                logger.error(f"Browser {index}: Error solving Turnstile: {str(e)}")
        finally:
            if self.debug:
                logger.debug(f"Browser {index}: Cleaning up")

            if route_handler:
                try:
                    await page.unroute("**/*", route_handler)
                except Exception:
                    pass

            try:
                if not self.proxy_support:
                    if solve_failed:
                        try:
                            await context.close()
                            new_context, new_page = await self._create_context_and_page(browser, config)
                            context, page = new_context, new_page
                            context_uses = 0
                            if self.debug:
                                logger.debug(f"Browser {index}: Context FORCE recycled after failure")
                        except Exception as recycle_error:
                            logger.warning(f"Browser {index}: Failed to recycle context after failure: {str(recycle_error)}")
                    else:
                        try:
                            await page.evaluate("""() => {
                                const overlay = document.getElementById('captcha-overlay');
                                if (overlay) overlay.remove();
                            }""")
                        except Exception:
                            pass
                        context_uses += 1

                        if context_uses >= self.context_max_uses:
                            recycled = False
                            try:
                                new_context, new_page = await self._create_context_and_page(browser, config)
                                await context.close()
                                context, page = new_context, new_page
                                context_uses = 0
                                recycled = True
                            except Exception as recycle_error:
                                context_uses = 0
                                logger.warning(f"Browser {index}: Failed to recycle context: {str(recycle_error)}")

                            if self.debug and recycled:
                                logger.debug(f"Browser {index}: Context recycled after max uses")

                    await self.context_pool.put((index, browser, context, page, config, context_uses))
                    if self.debug:
                        logger.debug(f"Browser {index}: Page returned to pool (use {context_uses}/{self.context_max_uses})")
                else:
                    await context.close()
                    await self.browser_pool.put((index, browser, config))
                    if self.debug:
                        logger.debug(f"Browser {index}: Context closed (proxy mode)")
            except Exception as e:
                if self.debug:
                    logger.warning(f"Browser {index}: Error during cleanup: {str(e)}")

    async def process_turnstile(self):
        url = request.args.get('url')
        sitekey = request.args.get('sitekey')
        action = request.args.get('action')
        cdata = request.args.get('cdata')

        if not url or not sitekey:
            return jsonify({
                "errorId": 1,
                "errorCode": "ERROR_WRONG_PAGEURL",
                "errorDescription": "Both 'url' and 'sitekey' are required"
            }), 200

        task_id = str(uuid.uuid4())
        await save_result(task_id, "turnstile", {
            "status": "CAPTCHA_NOT_READY",
            "createTime": int(time.time()),
            "url": url,
            "sitekey": sitekey,
            "action": action,
            "cdata": cdata
        })

        try:
            asyncio.create_task(self._solve_turnstile(task_id=task_id, url=url, sitekey=sitekey, action=action, cdata=cdata))

            if self.debug:
                logger.debug(f"Request completed with taskid {task_id}.")
            return jsonify({
                "errorId": 0,
                "task_id": task_id,
                "status": "accepted"
            }), 200
        except Exception as e:
            logger.error(f"Unexpected error processing request: {str(e)}")
            return jsonify({
                "errorId": 2,
                "errorCode": "ERROR_UNKNOWN",
                "errorDescription": str(e)
            }), 200

    async def get_result(self):
        task_id = request.args.get('id')

        if not task_id:
            return jsonify({
                "errorId": 3,
                "errorCode": "ERROR_WRONG_CAPTCHA_ID",
                "errorDescription": "Invalid task ID/Request parameter"
            }), 200

        result = await load_result(task_id)
        if not result:
            return jsonify({
                "errorId": 6,
                "status": "failure",
                "errorCode": "ERROR_CAPTCHA_FAIL",
                "errorDescription": "Workers could not solve the Captcha"
            }), 200

        if result == "CAPTCHA_NOT_READY" or (isinstance(result, dict) and result.get("status") == "CAPTCHA_NOT_READY"):
            return jsonify({"status": "processing"}), 200

        if isinstance(result, dict) and result.get("value") == "CAPTCHA_FAIL":
            return jsonify({
                "errorId": 5,
                "status": "failure",
                "errorCode": "ERROR_CAPTCHA_UNSOLVABLE",
                "errorDescription": "Workers could not solve the Captcha"
            }), 200

        if isinstance(result, dict) and result.get("value") and result.get("value") != "CAPTCHA_FAIL":
            return jsonify({
                "errorId": 0,
                "status": "success",
                "elapsed_time": result.get("elapsed_time", 0),
                "value": result["value"]
            }), 200

        return jsonify({
            "errorId": 1,
            "status": "failure",
            "errorCode": "ERROR_CAPTCHA_UNSOLVABLE",
            "errorDescription": "Workers could not solve the Captcha"
        }), 200

    @staticmethod
    async def index():
        return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Turnstile Solver API</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-900 text-gray-200 min-h-screen flex items-center justify-center">
                <div class="bg-gray-800 p-8 rounded-lg shadow-md max-w-2xl w-full border border-red-500">
                    <h1 class="text-3xl font-bold mb-6 text-center text-red-500">Welcome to Turnstile Solver API</h1>

                    <p class="mb-4 text-gray-300">To use the turnstile service, send a GET request to
                       <code class="bg-red-700 text-white px-2 py-1 rounded">/turnstile</code> with the following query parameters:</p>

                    <ul class="list-disc pl-6 mb-6 text-gray-300">
                        <li><strong>url</strong>: The URL where Turnstile is to be validated</li>
                        <li><strong>sitekey</strong>: The site key for Turnstile</li>
                    </ul>

                    <div class="bg-gray-700 p-4 rounded-lg mb-6 border border-red-500">
                        <p class="font-semibold mb-2 text-red-400">Example usage:</p>
                        <code class="text-sm break-all text-red-300">/turnstile?url=https://example.com&sitekey=sitekey</code>
                    </div>

                    <div class="bg-gray-700 p-4 rounded-lg mb-6">
                        <p class="text-gray-200 font-semibold mb-3">📢 Connect with Us</p>
                        <div class="space-y-2 text-sm">
                            <p class="text-gray-300">
                                📁 <strong>GitHub:</strong>
                                <a href="https://github.com/rythampkhandelwal" class="text-red-300 hover:underline">https://github.com/rythampkhandelwal</a>
                                - Source code and development
                            </p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
        """


def create_app(headless: bool, useragent: str, debug: bool, browser_type: str, thread: int, proxy_support: bool, context_max_uses: int = DEFAULT_CONTEXT_MAX_USES) -> Quart:
    server = TurnstileAPIServer(
        headless=headless,
        useragent=useragent,
        debug=debug,
        browser_type=browser_type,
        thread=thread,
        proxy_support=proxy_support,
        context_max_uses=context_max_uses,
    )
    return server.app


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', default='chromium')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--proxy', action='store_true')
    parser.add_argument('--headless', action='store_true', default=True)
    parser.add_argument('--threads', type=int, default=4)
    parser.add_argument('--port', type=int, default=5075)
    parser.add_argument('--context-max-uses', type=int, default=DEFAULT_CONTEXT_MAX_USES)
    args = parser.parse_args()

    app = create_app(
        headless=args.headless,
        debug=args.debug,
        useragent=None,
        browser_type=args.browser,
        thread=args.threads,
        proxy_support=args.proxy,
        context_max_uses=args.context_max_uses
    )
    app.run(host='0.0.0.0', port=args.port)
