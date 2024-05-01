import React from "react";
import Backdrop from "@mui/material/Backdrop";
import { Box, ThemeProvider } from "@mui/material";

const PublicationCountPopover = ({ open, onClose, publicationCount }) => {
  return (
    <Backdrop
      sx={{ color: "#fff", zIndex: (theme) => theme.zIndex.drawer + 1 }}
      open={open}
      onClick={onClose}
    >
      <ThemeProvider
        theme={{
          palette: {
            primary: {
              main: "#007FFF",
              dark: "#0066CC",
            },
          },
        }}
      >
        <Box
          sx={{
            minWidth: 210,
            minHeight: 50,
            borderRadius: 1,
            bgcolor: "#6750A4",
          }}
        >
          <p>
            Publication Count: <b>{publicationCount}</b>
          </p>
        </Box>
      </ThemeProvider>
    </Backdrop>
  );
};

export default PublicationCountPopover;
