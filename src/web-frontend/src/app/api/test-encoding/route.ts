
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const body = await request.json();
  const input = body.input;

  console.log('Received input:', input);

  return NextResponse.json({ output: input });
}
