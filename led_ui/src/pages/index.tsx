import Head from "next/head";

import Square from "~/pages/components/Square";
import Swatch from "~/pages/components/Swatch";

import { signal, computed, effect } from "@preact/signals-react";

export const inks = signal([[255,255,0],[255,0,0],[0,255,0],[0,0,255],[0,255,255]]);

export default function Home() {

  const squares = [];
  for (let y = 23; y >= 0; y--) {
    for (let x = 0; x < 24; x++) {
      squares.push(<Square key={`${x}-${y}`} x={x} y={y} />);
    }
  }

  return (
    <>
      <Head>
        <title>LED Board</title>
        <meta name="description" content="UI for LED Board" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-[#2e026d] to-[#15162c]">
        <div className="flex">
          <Swatch position={0} />
          <Swatch position={1} />
          <Swatch position={2} />
          <Swatch position={3} />
          <Swatch position={4} />
        </div>
        <div className="grid grid-cols-24 gap-1">
          {squares}
        </div>
      </main>
    </>
  );
}
