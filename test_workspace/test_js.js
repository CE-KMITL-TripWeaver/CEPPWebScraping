import puppeteer from "puppeteer-core";

const URL = "https://www.booking.com/";
const BROWSER_WS = "wss://brd-customer-hl_531c098e-zone-scraping_browser1:7pvq96qwj1bu@brd.superproxy.io:9222";

function addDays(date, days) {
  var result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

function toBookingTimestamp(date) {
  return date.toISOString().split('T')[0];
}

const search_text = "New York";
const now = new Date();
const check_in = toBookingTimestamp(addDays(now, 1));
const check_out = toBookingTimestamp(addDays(now, 2));

// This sample code searches Booking for acommodation in selected location
// and dates, then returns names, prices and rating for available options.

run(URL);

async function run(url) {
  console.log("Connecting to browser...");
  const browser = await puppeteer.connect({
    browserWSEndpoint: BROWSER_WS,
  });
  console.log("Connected! Navigate to site...");
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
  console.log("Navigated! Waiting for popup...");
  await close_popup(page);
  await interact(page);
  console.log("Parsing data...");
  const data = await parse(page);
  console.log(`Data parsed: ${JSON.stringify(data, null, 2)}`);
  await browser.close();
}

async function close_popup(page) {
  try {
    const close_btn = await page.waitForSelector('[aria-label="Dismiss sign-in info."]', { timeout: 25000, visible: true });
    console.log("Popup appeared! Closing...");
    await close_btn.click();
    console.log("Popup closed!");
  } catch (e) {
    console.log("Popup didn't appear.");
  }
}

async function interact(page) {
  console.log("Waiting for search form...");
  const search_input = await page.waitForSelector('[data-testid="destination-container"] input', { timeout: 60000 });
  console.log("Search form appeared! Filling it...");
  await search_input.type(search_text);
  await page.click('[data-testid="searchbox-dates-container"] button');
  await page.waitForSelector('[data-testid="searchbox-datepicker-calendar"]');
  await page.click(`[data-date="${check_in}"]`);
  await page.click(`[data-date="${check_out}"]`);
  console.log("Form filled! Submitting and waiting for result...");
  await Promise.all([
    page.click('button[type="submit"]'),
    page.waitForNavigation({ waitUntil: 'domcontentloaded' }),
  ]);
};

async function parse(page) {
  return await page.$$eval('[data-testid="property-card"]', els => els.map(el => {
    const name = el.querySelector('[data-testid="title"]')?.innerText;
    const price = el.querySelector('[data-testid="price-and-discounted-price"]')?.innerText;
    const review_score = el.querySelector('[data-testid="review-score"]')?.innerText ?? '';
    const [score_str, , , reviews_str = ''] = review_score.split('\n');
    const score = parseFloat(score_str) || score_str;
    const reviews = parseInt(reviews_str.replace(/\D/g, '')) || reviews_str;
    return { name, price, score, reviews };
  }));
}

