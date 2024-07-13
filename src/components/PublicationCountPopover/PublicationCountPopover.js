import React from "react";
import Backdrop from "@mui/material/Backdrop";
import { Box, ThemeProvider, Button, createTheme } from "@mui/material";

const theme = createTheme({
  palette: {
    primary: {
      main: "#007FFF",
      dark: "#0066CC",
    },
    grey: {
      50: "#fafafa",
      100: "#f5f5f5",
      200: "#eeeeee",
      300: "#e0e0e0",
      400: "#bdbdbd",
      500: "#9e9e9e",
      600: "#757575",
      700: "#616161",
      800: "#424242",
      900: "#212121",
    },
  },
});

const PublicationCountPopover = ({ open, onClose, publicationCount, onSubmit }) => {
  return (
    <Backdrop
      sx={{ color: "#fff", zIndex: (theme) => theme.zIndex.drawer + 1 }}
      open={open}
      onClick={onClose}
    >
      <ThemeProvider theme={theme}>
        <Box
          sx={{
            minWidth: 210,
            minHeight: 50,
            borderRadius: 1,
            bgcolor: "#6750A4",
            p: 2,
            textAlign: "center",
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <p>
            Publication Count: <b>{publicationCount}</b>
          </p>
          <Button variant="contained" onClick={onSubmit}>
            Submit
          </Button>
        </Box>
      </ThemeProvider>
    </Backdrop>
  );
};

export default PublicationCountPopover;
