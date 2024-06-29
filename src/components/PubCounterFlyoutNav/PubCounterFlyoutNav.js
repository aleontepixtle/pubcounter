// Filename - App.js

import * as React from "react";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import PubCounterDrawer from "../PubCounterDrawer/PubCounterDrawer";
import { Stack } from "@mui/material";

export default function ButtonAppBar() {
  return (
    <AppBar>
      <Stack>
        <Toolbar>
          <PubCounterDrawer></PubCounterDrawer>
          <Typography>PubCounter</Typography>
        </Toolbar>
      </Stack>
    </AppBar>
  );
}
