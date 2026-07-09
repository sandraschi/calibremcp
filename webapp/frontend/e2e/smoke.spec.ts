import { expect, test } from "@playwright/test";
const BE = "http://127.0.0.1:10720";
const FE = "http://127.0.0.1:10721";

test.describe("Fleet Audit", () => {
	test("Backend health", async ({ request }) => {
		const resp = await request.get(`${BE}/health`);
		expect(resp.status()).toBe(200);
	});

	test("Frontend loads", async ({ page }) => {
		await page.goto(FE, { timeout: 15000 });
		await page.waitForTimeout(3000);
		await expect(page.locator("#root")).toBeAttached();
	});
});

test.describe("API", () => {
	test("GET /api/system/status returns ok", async ({ request }) => {
		const resp = await request.get(
			`${BE}/api/system/status?status_level=basic`,
		);
		expect(resp.status()).toBe(200);
	});

	test("GET /api/libraries/stats returns stats", async ({ request }) => {
		const resp = await request.get(`${BE}/api/libraries/stats`);
		expect(resp.status()).toBe(200);
		const body = await resp.json();
		expect(body).toHaveProperty("total_books");
	});

	test("GET /api/authors returns list", async ({ request }) => {
		const resp = await request.get(`${BE}/api/authors?limit=5`);
		expect(resp.status()).toBe(200);
	});
});

test.describe("Navigation", () => {
	test("Dashboard page loads with KPI cards", async ({ page }) => {
		await page.goto(FE, { timeout: 15000 });
		await page.waitForTimeout(3000);
		await expect(page.locator("h1")).toContainText("Overview");
	});

	test("Books page loads", async ({ page }) => {
		await page.goto(`${FE}/books`, { timeout: 15000 });
		await page.waitForTimeout(3000);
		await expect(page.locator("body")).toBeAttached();
	});

	test("Help page loads", async ({ page }) => {
		await page.goto(`${FE}/help`, { timeout: 15000 });
		await page.waitForTimeout(3000);
		await expect(page.locator("body")).toBeAttached();
	});

	test("Chat page loads", async ({ page }) => {
		await page.goto(`${FE}/chat`, { timeout: 15000 });
		await page.waitForTimeout(3000);
		await expect(page.locator("body")).toBeAttached();
	});

	test("No console errors on dashboard", async ({ page }) => {
		const errors: string[] = [];
		page.on("pageerror", (err) => errors.push(err.message));
		await page.goto(FE, { timeout: 15000 });
		await page.waitForTimeout(3000);
		expect(errors).toHaveLength(0);
	});
});
