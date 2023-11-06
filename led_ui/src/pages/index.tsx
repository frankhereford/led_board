import Head from "next/head";

import React, { useEffect, useState, useContext } from 'react';

import Square from "~/pages/components/Square";
import Swatch from "~/pages/components/Swatch";
import ColorPicker from "~/pages/components/ColorPicker";

import { AppContext } from '~/pages/contexts/AppContext';

import { api } from "~/utils/api";

import dynamic from 'next/dynamic';
import { relative } from "path";

const EmojiPicker = dynamic(() => import('emoji-picker-react').then((mod) => mod.default), {
  ssr: false,
});

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
  for (let y = 0; y < 24; y++) {
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

  const setEmoji = (emoji: string, event: MouseEvent) => {
    renderEmoji.mutate(emoji);
  }


  return (
    <>
      <Head>
        <title>LED Board</title>
        <meta name="description" content="UI for LED Board" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main
        className="flex flex-row min-h-screen items-center justify-center bg-gradient-to-b from-[#C6C1B7] to-[#C6C1B7]"
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
      >
        <img src='/draw-on-me.png' style={{
          position: 'absolute',
          top: 0,
          width: '200px',
          zIndex: 0,

        }} />

        <div className="flex justify-center basis-1/2 flex-1 z-10">
          <div className="grid grid-cols-24 gap-1 bg-neutral-900" style={{ width: "548px"}}>
            {squares}
          </div>
        </div>
        <div className="basis-1/2 flex-auto">
          
          <div className="flex flex-row">

            <div className="basis-1/4">
              <div className="flex flex-col">
                <Swatch position={0} />
                <Swatch position={1} />
                <Swatch position={2} />
                <Swatch position={3} />
                <Swatch position={4} />
                <Swatch position={5} />
                <Swatch position={6} />
                <Swatch position={7} />
                <div>
                  <button
                    className="my-4 mx-1 w-36 h-12 rounded-full bg-slate-500 hover:bg-red-500 text-slack-900 font-bold"
                    style={{
                      position: 'relative',
                      left: '-22px',
                    }}
                    onClick={clearTheBoard}
                  >
                    📄
                  </button>
                </div>
              </div>
            </div>


            <div className='basis-3/4'>
              <div>
                <ColorPicker />
              </div>
              <div>
                <EmojiPicker
                  width={387}
                  height={460}
                  onEmojiClick={setEmoji} />
              </div>
            </div>

          </div>

        </div>

      </main>
    </>
  );
}
