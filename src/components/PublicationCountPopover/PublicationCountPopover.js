import React, { useState } from "react";
import Backdrop from "@mui/material/Backdrop";
import {
  Box,
  ThemeProvider,
  Button,
  createTheme,
  IconButton,
  TextField,
  Stack,
} from "@mui/material";
import EditTwoToneIcon from "@mui/icons-material/EditTwoTone";
import SaveIcon from "@mui/icons-material/Save";
import CancelIcon from "@mui/icons-material/Cancel";

const theme = createTheme({
  palette: {
    primary: {
      main: "#FFF",
      dark: "#FFF",
    },
    white: {
      main: "#FFF",
    },
    submit: {
      main: "#FFC72C",
    },
  },
});

const PublicationCountPopover = ({
  open,
  onClose,
  publicationCount,
  onSubmit,
  onSaveModifiedCount, // Handler for saving modified count
}) => {
  const [isEditing, setIsEditing] = useState(false); // Track edit state
  const [editedCount, setEditedCount] = useState(publicationCount); // Track edited count

  // Handle entering edit state
  const handleEdit = () => {
    setIsEditing(true);
  };

  // Handle saving changes
  const handleSave = () => {
    onSaveModifiedCount(editedCount); // Pass the modified count back to the parent
    setIsEditing(false);
  };

  // Handle canceling changes
  const handleCancel = () => {
    setEditedCount(publicationCount); // Revert to original count
    setIsEditing(false);
  };

  // Prevent dismissal in edit state
  const handleBackdropClick = () => {
    if (!isEditing) onClose();
  };

  return (
    <Backdrop
      sx={{ color: "#fff", zIndex: (theme) => theme.zIndex.drawer + 1 }}
      open={open}
      onClick={handleBackdropClick}
    >
      <ThemeProvider theme={theme}>
        <Box
          sx={{
            minWidth: 220,
            minHeight: 50,
            borderRadius: 1,
            background: "linear-gradient(90deg, #1CB5E0 0%, #000851 100%)",
            p: 2,
            textAlign: "center",
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {!isEditing ? (
            <>
              <Stack
                direction="row"
                spacing={0}
                sx={{
                  justifyContent: "center",
                  alignItems: "center",
                }}
              >
                <p>
                  Publication Count: <b>{editedCount}</b>
                </p>
                <IconButton onClick={handleEdit}>
                  <EditTwoToneIcon color="white" />
                </IconButton>
              </Stack>
              <Button variant="contained" onClick={onSubmit} color="submit">
                Submit
              </Button>
            </>
          ) : (
            <>
              <TextField
                label="Edit Publication Count"
                type="number"
                value={editedCount}
                onChange={(e) => setEditedCount(e.target.value)}
                fullWidth
                autoFocus
                InputProps={{
                  sx: {
                    color: "white", // Text color inside the input
                    "& .MuiOutlinedInput-root": {
                      color: "white", // Text color
                      fontFamily: "Arial",
                      fontWeight: "bold",
                      backgroundColor: "transparent", // Optional background
                      "& fieldset": {
                        borderColor: "white", // Default border color (white)
                      },
                      "&:hover fieldset": {
                        borderColor: "white", // Keep border white on hover
                      },
                      "&.Mui-focused fieldset": {
                        borderColor: "white", // Keep border white on focus
                      },
                    },
                  },
                }}
                InputLabelProps={{
                  sx: {
                    color: "white", // Label color
                  },
                }}
              />

              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSave}
                  sx={{ mr: 1 }}
                >
                  Save
                </Button>
                <Button
                  variant="contained"
                  startIcon={<CancelIcon />}
                  onClick={handleCancel}
                >
                  Cancel
                </Button>
              </Box>
            </>
          )}
        </Box>
      </ThemeProvider>
    </Backdrop>
  );
};

export default PublicationCountPopover;
