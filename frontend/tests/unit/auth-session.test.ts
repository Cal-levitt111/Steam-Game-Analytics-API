import { describe, expect, test } from "vitest";

import { ApiError } from "@/lib/api/client";
import { toErrorResponse } from "@/lib/auth/session";

describe("auth session helpers", () => {
  test("toErrorResponse clears the auth cookie on auth failures", () => {
    const error = new ApiError(
      401,
      {
        code: "TOKEN_EXPIRED",
        message: "Expired.",
        detail: null,
      },
      null,
    );

    const response = toErrorResponse(error);
    const cookieHeader = response.headers.get("set-cookie");

    expect(response.status).toBe(401);
    expect(cookieHeader).toContain("sga_session=");
    expect(cookieHeader).toContain("Max-Age=0");
  });
});
