import { NextRequest, NextResponse } from "next/server";

export function GET(request: NextRequest) {
  const ticker = (request.nextUrl.searchParams.get("ticker") || "").toUpperCase();
  if (!/^[A-Z]{4,5}$/.test(ticker)) return NextResponse.redirect(new URL("/", request.url));
  return NextResponse.redirect(new URL(`/stocks/${ticker}`, request.url));
}
