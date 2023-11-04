import React from 'react';

interface SquareProps {
  x: number;
  y: number;
}

const Square: React.FC<SquareProps> = ({ x, y }) => {
  const [r, setR] = React.useState<number>(0);
  const [g, setG] = React.useState<number>(0);
  const [b, setB] = React.useState<number>(0);

  // Ensure x and y are positive integers
  if (x < 0 || y < 0 || !Number.isInteger(x) || !Number.isInteger(y)) {
    return <div>Props x and y must be positive integers.</div>;
  }

  return (
    <div
      style={{
        width: '100px',
        height: '100px',
        backgroundColor: `rgb(${r}, ${g}, ${b})`,
      }}
    >
    </div>
  );
};

export default Square;
