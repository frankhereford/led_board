import Head from "next/head";

import React, { useEffect } from 'react';

import Square from "~/pages/components/Square";
import Swatch from "~/pages/components/Swatch";
import ColorPicker from "~/pages/components/ColorPicker";

import { useContext } from 'react';
import { AppContext } from '~/pages/contexts/AppContext';

export default function Home() {

  const { colorArrays, setColorArrays, isMouseDown, setIsMouseDown } = useContext(AppContext);

  useEffect(() => {
    // Establish the WebSocket connection
    const websocket = new WebSocket('ws://10.10.10.1:3001/ws');

    websocket.onopen = () => {
      console.log('WebSocket Connected');
    };

    websocket.onmessage = (event) => {
      console.log('Received:', event.data);
    };

    websocket.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };

    websocket.onclose = () => {
      console.log('WebSocket Disconnected');
    };

    return () => {
      websocket.close();
    };
  }, []);



  const squares = [];
  for (let y = 23; y >= 0; y--) {
    for (let x = 0; x < 24; x++) {
      squares.push(<Square key={`${x}-${y}`} x={x} y={y} color={[10,0,0]} />);
    }
  }

  const handleMouseDown = () => {
    setIsMouseDown(true);
  }

  const handleMouseUp= () => {
    setIsMouseDown(false);
  }

  return (
    <>
      <Head>
        <title>LED Board</title>
        <meta name="description" content="UI for LED Board" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main
        className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-[#2e026d] to-[#15162c]"
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
      >

        <div className="grid grid-cols-24 gap-1">
          {squares}
        </div>
        <div className="flex">
          <Swatch position={0} />
          <Swatch position={1} />
          <Swatch position={2} />
          <Swatch position={3} />
          <Swatch position={4} />
        </div>
        <div>
          <ColorPicker />
        </div>

      </main>
    </>
  );
}
