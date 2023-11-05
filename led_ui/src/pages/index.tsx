import Head from "next/head";

import React, { useEffect, useState, useContext } from 'react';

import Square from "~/pages/components/Square";
import Swatch from "~/pages/components/Swatch";
import ColorPicker from "~/pages/components/ColorPicker";

import { AppContext } from '~/pages/contexts/AppContext';

import { api } from "~/utils/api";

export default function Home() {
  
  const clearBoard = api.square.clearBoard.useMutation({});
  const renderEmoji = api.square.setEmoji.useMutation({});
  const getBoard = api.square.getBoard.useQuery();

  const [squareColors, setSquareColors] = useState(() =>
    Array(24).fill(null).map(() => Array(24).fill([0, 0, 0]))
  );

  const { colorArrays, setColorArrays, isMouseDown, setIsMouseDown } = useContext(AppContext);

  useEffect(() => {
    if (getBoard.data) {
      for (let y = 0; y < getBoard.data.length; y++) {
        for (let x = 0; x < getBoard.data.length; x++) {
          setColorAt(x, y, getBoard.data[y]![x]!.color)
        }
      }
    }
  }, [getBoard.data]);

  useEffect(() => {
    const websocket = new WebSocket('ws://10.10.10.1:3001/ws');

    websocket.onopen = () => {
      console.log('WebSocket Connected');
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log(data)
      if (data.clear) {
        console.log('in clear')
        getBoard.refetch();
      } else {
        setColorAt(data.x, data.y, data.color);
      }
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

  const setColorAt = (x: number, y: number, color: number[]) => {
    //console.log(`Setting color at ${x}, ${y} to ${color}`);
    setSquareColors((prevColors) => {
      const newColors = [...prevColors];
      newColors[y]![x] = color;
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
        color={squareColors[y]![x]}
      />);
    }
  }

  const handleMouseDown = () => {
    setIsMouseDown(true);
  }

  const handleMouseUp= () => {
    setIsMouseDown(false);
  }

  const clearTheBoard = () => {
    clearBoard.mutate();
  }

  const setEmoji = () => {
    renderEmoji.mutate({emoji: '👍'});
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

        <div>
          <button
            className="bg-slate-300 hover:bg-red-700 text-slack-900 font-bold py-2 px-4 rounded"
            onClick={clearTheBoard}
          >
            Clear
          </button>
        </div>
        <div>
          <button
            className="bg-slate-300 hover:bg-red-700 text-slack-900 font-bold py-2 px-4 rounded"
            onClick={setEmoji}
          >
            👍
          </button>
        </div>



      </main>
    </>
  );
}
