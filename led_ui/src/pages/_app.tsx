import { type AppType } from "next/app";

import { api } from "~/utils/api";

import { AppProvider } from '~/pages/contexts/AppContext';

import "~/styles/globals.css";

const MyApp: AppType = ({ Component, pageProps }) => {
  return (
    <AppProvider>
      <Component {...pageProps} />
    </AppProvider>
  )
};

export default api.withTRPC(MyApp);
