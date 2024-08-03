import React, { useState, useEffect } from "react";
import Backdrop from "@mui/material/Backdrop";
import {
  Box,
  ThemeProvider,
  Button,
  createTheme,
  IconButton,
  TextField,
  InputAdornment,
  Typography,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";

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
  components: {
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            "& fieldset": {
              borderColor: "white", // Default border color
            },
            "&:hover fieldset": {
              borderColor: "yellow", // Border color on hover
            },
            "&.Mui-focused fieldset": {
              borderColor: "white", // Border color when focused
            },
          },
          "& .MuiInputBase-input": {
            color: "white", // Text color
          },
          "& .MuiInputLabel-root": {
            color: "white", // Label color
          },
        },
      },
    },
  },
});

const PublicationCountPopover = ({
  open,
  onClose,
  publicationCount,
  onSubmit,
  onAddMore,
  onDoneAdding, // New prop for Done Adding button
  totalPublications,
  onEditTotal,
  isPublicationSelected, // New prop to determine if a publication is selected
  isAddingMore, // New prop to determine if user is adding more
}) => {
  const [editMode, setEditMode] = useState(false);
  const [localTotal, setLocalTotal] = useState(totalPublications);

  useEffect(() => {
    setLocalTotal(totalPublications);
  }, [totalPublications]);

  const handleTotalChange = (event) => {
    let value = event.target.value;
    if (value === "") {
      setLocalTotal("");
      onEditTotal(0);
      return;
    }
    value = value.replace(/\D/g, ""); // Remove non-digit characters
    setLocalTotal(parseInt(value, 10));
    onEditTotal(parseInt(value, 10));
  };

  const toggleEditMode = () => {
    if (editMode && localTotal === "") {
      setLocalTotal(totalPublications);
    }
    setEditMode((prev) => !prev);
  };

  const displayTotalPublications = isAddingMore
    ? totalPublications
    : localTotal;

  return (
    <Backdrop
      sx={{ color: "#fff", zIndex: (theme) => theme.zIndex.drawer + 1 }}
      open={open}
      onClick={(e) => {
        if (isAddingMore) {
          e.stopPropagation();
        } else {
          onClose();
        }
      }}
    >
      <ThemeProvider theme={theme}>
        <Box
          sx={{
            minWidth: 300, // Adjusted the minWidth
            minHeight: 200, // Adjusted the minHeight
            borderRadius: 1,
            p: 2,
            textAlign: "center",
            background: 'linear-gradient(90deg, #1CB5E0 0%, #000851 100%)'// Gradient background
          }}
          onClick={(e) => e.stopPropagation()} // Prevent closing on box click
        >
          <p>
            Publication Count: <b>{publicationCount}</b>
          </p>
          <>
            <Button
              variant="contained"
              onClick={onAddMore}
              sx={{ m: 1, bgcolor: "#ffbd03" }}
            >
              Add More
            </Button>
            {isPublicationSelected && !isAddingMore && (
              <Button
                variant="contained"
                onClick={onSubmit}
                sx={{ m: 1, bgcolor: "#ffbd03" }}
              >
                Submit
              </Button>
            )}
          </>
          {isAddingMore && ( // Show Done Adding button if adding more
            <Button
              variant="contained"
              onClick={onDoneAdding}
              sx={{ m: 1, bgcolor: "#ffbd03" }}
            >
              Done Adding
            </Button>
          )}
          <Box sx={{ mt: 2 }}>
            {editMode ? (
              <TextField
                label="Total Publications"
                variant="outlined"
                size="small"
                value={localTotal}
                onChange={handleTotalChange}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    "& fieldset": {
                      borderColor: "white", // Default border color
                    },
                    "&:hover fieldset": {
                      borderColor: "yellow", // Border color on hover
                    },
                    "&.Mui-focused fieldset": {
                      borderColor: "white", // Border color when focused
                    },
                  },
                  "& .MuiInputBase-input": {
                    color: "white", // Text color
                  },
                  "& .MuiInputLabel-root": {
                    color: "white", // Label color
                  },
                }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={toggleEditMode}>
                        <EditIcon sx={{ color: "white" }} />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            ) : (
              <Box display="flex" alignItems="center" justifyContent="center">
                <Typography variant="body1" sx={{ color: "white" }}>
                  Total Publications to Submit:{" "}
                  <b>{displayTotalPublications}</b>
                </Typography>
                <IconButton onClick={toggleEditMode}>
                  <EditIcon sx={{ color: "white" }} />
                </IconButton>
              </Box>
            )}
          </Box>
        </Box>
      </ThemeProvider>
    </Backdrop>
  );
};

export default PublicationCountPopover;
