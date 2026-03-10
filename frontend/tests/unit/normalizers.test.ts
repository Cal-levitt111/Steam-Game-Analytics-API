import { describe, expect, test } from "vitest";

import {
  buildQueryString,
  normalizeApiError,
  parseAnalyticsEnvelope,
  parseDirectModel,
  parsePaginatedEnvelope,
  parseWrappedData,
} from "@/lib/api/normalizers";

describe("api normalizers", () => {
  test("buildQueryString omits empty values and joins arrays", () => {
    expect(
      buildQueryString({
        q: "action",
        page: 2,
        tags: ["indie", "co-op"],
        empty: "",
        skip: undefined,
      }),
    ).toBe("?q=action&page=2&tags=indie%2Cco-op");
  });

  test("normalizeApiError preserves backend envelope", () => {
    const response = new Response(null, { status: 409, statusText: "Conflict" });
    const payload = {
      error: {
        code: "CONFLICT",
        message: "Already present.",
        detail: { value: 1 },
      },
    };

    expect(normalizeApiError(payload, response)).toEqual(payload.error);
  });

  test("parse helpers accept expected response shapes", () => {
    expect(parsePaginatedEnvelope({ data: [1, 2], pagination: { page: 1 } })).toEqual({
      data: [1, 2],
      pagination: { page: 1 },
    });
    expect(parseAnalyticsEnvelope({ data: [{ value: 1 }], generated_at: "now", query_params: {} })).toEqual({
      data: [{ value: 1 }],
      generated_at: "now",
      query_params: {},
    });
    expect(parseWrappedData({ data: { id: 1 } })).toEqual({ data: { id: 1 } });
    expect(parseDirectModel({ id: 1, name: "Game" })).toEqual({ id: 1, name: "Game" });
  });
});
