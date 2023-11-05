import Head from "next/head";

import React, { useEffect, useState, useContext } from 'react';

import Square from "~/pages/components/Square";
import Swatch from "~/pages/components/Swatch";
import ColorPicker from "~/pages/components/ColorPicker";

import { AppContext } from '~/pages/contexts/AppContext';

import { api } from "~/utils/api";

export default function Home() {
  
  const getBoard = api.square.getBoard.useQuery();

  const [squareColors, setSquareColors] = useState(() =>
    Array(24).fill(null).map(() => Array(24).fill([0, 0, 0]))
  );

  const { colorArrays, setColorArrays, isMouseDown, setIsMouseDown } = useContext(AppContext);

  
  useEffect(() => {
    //console.log(getBoard.data);
    if (getBoard.data) {
      for (let y = 0; y < getBoard.data.length; y++) {
        for (let x = 0; x < getBoard.data.length; x++) {
          //console.log(getBoard.data[y]![x])
          setColorAt(x, y, getBoard.data[y]![x]!)
        }
      }
    }
  
  }, [getBoard.data]);

  useEffect(() => {
    // Establish the WebSocket connection
    const websocket = new WebSocket('ws://10.10.10.1:3001/ws');

    websocket.onopen = () => {
      console.log('WebSocket Connected');
    };

    websocket.onmessage = (event) => {
      //console.log('Received:', event.data);
      const data = JSON.parse(event.data);
      //console.log(data);
      setColorAt(data.x, data.y, data.color);
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

  // Function to update the color of a square
  const setColorAt = (x: number, y: number, color: number[]) => {
    //console.log(`Setting color at ${x}, ${y} to ${color}`);
    setSquareColors((prevColors) => {
      const newColors = [...prevColors];
      newColors[y]![x] = color; // assuming the first index is Y and the second index is X
      return newColors;
    });
  };


  const squares = [];
  for (let y = 23; y >= 0; y--) {
    for (let x = 0; x < 24; x++) {
      squares.push(<Square
        key={`${x}-${y}`}
        x={x}
        y={y}
        color={squareColors[y]![x]} // Pass the color from state
      />);
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
