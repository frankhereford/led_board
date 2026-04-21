import { createContext, useContext, useState, ReactNode, Dispatch, SetStateAction } from 'react';

type AppContextType = {
  colorArrays: number[][];
  setColorArrays: Dispatch<SetStateAction<number[][]>>;
  isMouseDown: boolean;
  setIsMouseDown: Dispatch<SetStateAction<boolean>>;
  activeSwatch: number;
  setActiveSwatch: Dispatch<SetStateAction<number>>;
};

const defaultValues: AppContextType = {
  colorArrays: [[255, 255, 255], [255, 0, 0], [0, 255, 0], [0, 0, 255], [255,255,0], [255, 0, 255], [0, 255, 255], [0, 0, 0]],
  setColorArrays: () => { },
  isMouseDown: false,
  setIsMouseDown: () => { },
  activeSwatch: 0,
  setActiveSwatch: () => { },
};

export const AppContext = createContext<AppContextType>(defaultValues);

type AppProviderProps = {
  children: ReactNode;
};

export const AppProvider = ({ children }: AppProviderProps) => {
  const [colorArrays, setColorArrays] = useState<number[][]>(defaultValues.colorArrays);
  const [isMouseDown, setIsMouseDown] = useState<boolean>(defaultValues.isMouseDown);
  const [activeSwatch, setActiveSwatch] = useState<number>(defaultValues.activeSwatch); // New state variable added here

  return (
    <AppContext.Provider value={{ colorArrays, setColorArrays, isMouseDown, setIsMouseDown, activeSwatch, setActiveSwatch }}>
      {children}
    </AppContext.Provider>
  );
};