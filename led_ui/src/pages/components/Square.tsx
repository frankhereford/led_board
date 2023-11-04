import React from 'react';
import { signal } from "@preact/signals-react";

interface SquareProps {
  x: number;
  y: number;
}

const color = signal([0,0,0])

const Square: React.FC<SquareProps> = ({ x, y }) => {

  // Function to generate an array of 3 random numbers between 0 and 255
  const randomizeColor = () => {
    color.value = [0, 1, 2].map(() => Math.floor(Math.random() * 256));
  };

  // Ensure x and y are positive integers
  if (x < 0 || y < 0 || !Number.isInteger(x) || !Number.isInteger(y)) {
    return <div>Props x and y must be positive integers.</div>;
  }

  return (
    <div
      style={{
        width: '100px',
        height: '100px',
        backgroundColor: `rgb(${color.value[0]}, ${color.value[1]}, ${color.value[2]})`,
      }}
      onClick={randomizeColor} // Attached randomizeColor to the onClick event
    >
    </div>
  );
};

export default Square;
