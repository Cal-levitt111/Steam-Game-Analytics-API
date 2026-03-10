import { expect, test } from "@playwright/test";

function uniqueEmail() {
  return `demo-${Date.now()}-${Math.random().toString(36).slice(2, 8)}@example.com`;
}

test("redirects anonymous users to the auth page", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/auth$/);
  await expect(page.getByRole("heading", { name: /sign in to test collections and authenticated flows/i })).toBeVisible();
});

test("supports auth and collection membership flows", async ({ page }) => {
  const email = uniqueEmail();
  const collectionName = `Demo Collection ${Date.now()}`;

  await page.goto("/auth");
  await page.getByRole("button", { name: /^register$/i }).click();
  await page.getByLabel(/display name/i).fill("Demo Tester");
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/password/i).fill("StrongPass123");
  await page.getByRole("button", { name: /create account/i }).click();

  await expect(page).toHaveURL(/\/collections$/);
  await page.getByLabel(/^name$/i).fill(collectionName);
  await page.getByLabel(/description/i).fill("Collection created during Playwright verification.");
  await page.getByRole("button", { name: /create collection/i }).click();

  await expect(page).toHaveURL(/\/collections\/\d+$/, { timeout: 15_000 });
  await expect(page.getByRole("heading", { name: collectionName })).toBeVisible();

  await page.goto("/games");
  await page.locator('a[href^="/games/"]').first().click();
  await page.getByRole("button", { name: /add to collection/i }).click();
  await expect(page.getByText(/game added to collection/i)).toBeVisible();

  await page.goto("/search?q=action");
  await expect(page.getByRole("heading", { name: /search game metadata/i })).toBeVisible();
  await expect(page.getByText(/search results|no results matched your query/i).first()).toBeVisible();

  await page.goto("/analytics");
  await expect(page.getByRole("heading", { name: /explore the api's aggregate endpoints/i })).toBeVisible();

  await page.goto("/collections");
  await page.getByRole("link", { name: collectionName }).click();
  await page.getByRole("button", { name: /remove from collection/i }).click();
  await expect(page.getByText(/this collection is empty/i)).toBeVisible();
});
