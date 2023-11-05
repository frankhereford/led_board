import React, { useEffect, useState } from 'react';
import { inks } from "~/pages/index";
import { signal, computed, effect } from "@preact/signals-react";

import { api } from "~/utils/api";

interface SquareProps {
  x: number;
  y: number;
}

//const color = signal([0,0,0])

// Logs name every time it changes:
//effect(() => console.log(color.value));

const Square: React.FC<SquareProps> = ({ x, y }) => {
  const setColor = api.square.color.useMutation({});

  const [squareColor, setSquareColor] = useState<number[]>([0,0,0]);


  useEffect(() => {
    setColor.mutate({ x: x, y: y, color: squareColor })
  }, [squareColor]);


  // Function to generate an array of 3 random numbers between 0 and 255
  const getColor = () => {
    setSquareColor(inks.value[0]!)
  };

  return (
    <div
      style={{
        width: '20px',
        height: '20px',
        backgroundColor: `rgb(${squareColor[0]}, ${squareColor[1]}, ${squareColor[2]})`,
      }}
      onMouseEnter={getColor} // Attached randomizeColor to the onClick event
    >
    </div>
  );
};

export default Square;
