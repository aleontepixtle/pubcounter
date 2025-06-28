import React, { useState, useEffect } from "react";
import "./PublicationCounter.css";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Divider from "@mui/material/Divider";
import OutlinedInput from "@mui/material/OutlinedInput";
import InputAdornment from "@mui/material/InputAdornment";
import FormHelperText from "@mui/material/FormHelperText";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import Typography from "@mui/material/Typography";
import ScaleIcon from "@mui/icons-material/ScaleOutlined";
import Box from "@mui/material/Box";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import PublicationCountPopover from "../PublicationCountPopover/PublicationCountPopover";
import PublicationSearch from "../PublicationSearch/PublicationSearch";
import {
  database,
  ref,
  set,
  get,
} from "../PublicationSearch/firebase/firebase";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { Snackbar, Alert } from "@mui/material";

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

const PublicationCounter = () => {
  const [unitOfMeasureWeight, setUnitOfMeasureWeight] = useState(0);
  const [totalWeightOfBatch, setTotalWeightOfBatch] = useState(0);
  const [selectedUnitOfMeasureCount, setSelectedCount] = useState(1);
  const [publicationCount, setPublicationCount] = useState(null);
  const [popoverOpen, setPopoverOpen] = useState(false);
  const [selectedPublication, setSelectedPublication] = useState(null);
  const [previousPublication, setPreviousPublication] = useState(null);
  const [isModified, setIsModified] = useState(false);
  const [dbCache, setDbCache] = useState(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "info",
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const snapshot = await get(ref(database));
        if (snapshot.exists()) {
          setDbCache(snapshot.val());
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
    fetchData();
  }, []);

  const handleInputChange = (e) => {
    let { value } = e.target;
    value = value.replace(/\D|^0+/g, "");
    value = value === "" ? "" : parseInt(value);
    setTotalWeightOfBatch(value);
  };

  const handleUnitOfMeasureWeightChange = (e) => {
    let { value } = e.target;
    value = value.replace(/\D|^0+/g, "");
    value = value === "" ? "" : parseInt(value);
    setUnitOfMeasureWeight(value);
  };

  const handleCountChange = (e) => {
    setSelectedCount(parseInt(e.target.value));
  };

  const calculatePublicationCount = () => {
    if (
      !unitOfMeasureWeight ||
      !totalWeightOfBatch ||
      !selectedUnitOfMeasureCount
    ) {
      setSnackbar({
        open: true,
        message: "Please enter valid values for all fields.",
        severity: "warning",
      });
      return;
    }

    const calculatedCount =
      (totalWeightOfBatch / unitOfMeasureWeight) * selectedUnitOfMeasureCount;
    setPublicationCount(Math.round(calculatedCount));
    setIsModified(false); // Reset modified flag since we're recalculating
    togglePopover();
  };

  const handleSaveModifiedCount = (newCount) => {
    setPublicationCount(newCount); // Update the count with the new modified value
    setIsModified(true); // Mark the count as modified
  };

  const togglePopover = () => {
    setPopoverOpen(!popoverOpen);
  };

  // Reset the count and recalculate when the popover is dismissed
  const handlePopoverClose = () => {
    setPublicationCount(null); // Clear the count
    calculatePublicationCount(); // Recalculate the count based on the input values
    setPopoverOpen(false); // Close the popover
    setPublicationCount(null); // Clear the count if it was modified
  };

  const handleSubmit = async () => {
    if (selectedPublication && dbCache) {
      try {
        const publicationIndex = Object.keys(dbCache).find(
          (key) => dbCache[key].jwId === selectedPublication.jwId
        );

        if (publicationIndex !== undefined) {
          const perPublicationWeight = unitOfMeasureWeight / selectedUnitOfMeasureCount;

          const updatedPublication = {
            ...dbCache[publicationIndex],
            quantity: publicationCount,
            unitWeight: perPublicationWeight,
          };

          await set(ref(database, `${publicationIndex}`), updatedPublication);
          setSnackbar({
            open: true,
            message: "Publication quantity updated successfully!",
            severity: "success",
          });

          // Update cache
          setDbCache({
            ...dbCache,
            [publicationIndex]: updatedPublication,
          });
        } else {
          setSnackbar({
            open: true,
            message: `Publication with ID ${selectedPublication.jwId} not found`,
            severity: "error",
          });
        }
      } catch (error) {
        console.error("Error updating publication:", error);
        setSnackbar({
          open: true,
          message: "Failed to update publication",
          severity: "error",
        });
      }
    } else {
      setSnackbar({
        open: true,
        message: "Please select a publication",
        severity: "warning",
      });
    }
  };

  const handlePublicationSelect = (publication) => {
    if (publication === null) {
      // Clear the values if the selected publication is cleared
      setUnitOfMeasureWeight(0); // Clear Unit of Measure
      setTotalWeightOfBatch(0); // Clear Total Weight of Batch
    } else if (publication !== previousPublication) {
      // If a different publication is selected, reset the fields
      setUnitOfMeasureWeight(0); // Reset Unit of Measure
      setTotalWeightOfBatch(0); // Reset Total Weight of Batch
    }

    setPreviousPublication(publication); // Update previousPublication to the new one (or null)
    setSelectedPublication(publication); // Update selectedPublication (or null)
  };

  return (
    <ThemeProvider theme={theme}>
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="60vh"
        p={4}
      >
        <Stack
          direction="column"
          divider={<Divider orientation="vertical" flexItem />}
          spacing={3}
          justifyContent="center"
          alignItems="center"
        >
          <Stack
            direction="column"
            spacing={3}
            justifyContent="center"
            alignItems="center"
          >
            <Typography variant="overline text" component="h1">
              Publication Counter Calculator
            </Typography>
            <ScaleIcon />
            <PublicationSearch onPublicationSelect={handlePublicationSelect} />
          </Stack>

          <Stack direction="column" spacing={3}>
            <Typography variant="overline" display="block" gutterBottom>
              How many in the Unit of Measure?
            </Typography>
            <FormControl>
              <RadioGroup
                row
                aria-labelledby="demo-row-radio-buttons-group-label"
                name="row-radio-buttons-group"
                value={selectedUnitOfMeasureCount.toString()}
                onChange={handleCountChange}
              >
                <FormControlLabel value="1" control={<Radio />} label="1" />
                <FormControlLabel value="2" control={<Radio />} label="2" />
                <FormControlLabel value="5" control={<Radio />} label="5" />
                <FormControlLabel value="10" control={<Radio />} label="10" />
              </RadioGroup>
            </FormControl>
          </Stack>
          <Stack direction="row" spacing={2}>
            <Typography variant="overline" display="block" gutterBottom>
              Enter Unit of Measure
            </Typography>
            <FormControl sx={{ m: 0, width: "13ch" }} variant="outlined">
              <OutlinedInput
                id="outlined-adornment-weight"
                type="number"
                size="small"
                value={unitOfMeasureWeight}
                onChange={handleUnitOfMeasureWeightChange}
                endAdornment={<InputAdornment position="end">g</InputAdornment>}
                aria-describedby="outlined-weight-helper-text"
                inputProps={{
                  "aria-label": "weight",
                  onFocus: () => setUnitOfMeasureWeight(""),
                }}
              />
              <FormHelperText id="outlined-weight-helper-text">
                Weight
              </FormHelperText>
            </FormControl>
          </Stack>
          <Stack direction="row" spacing={2}>
            <Typography variant="overline" display="block" gutterBottom>
              Enter Total Weight of Batch
            </Typography>
            <FormControl sx={{ m: 0, width: "13ch" }} variant="outlined">
              <OutlinedInput
                id="outlined-adornment-weight"
                type="number"
                size="small"
                value={totalWeightOfBatch}
                onChange={handleInputChange}
                endAdornment={<InputAdornment position="end">g</InputAdornment>}
                aria-describedby="outlined-weight-helper-text"
                inputProps={{
                  "aria-label": "weight",
                  onFocus: () => setTotalWeightOfBatch(""),
                }}
              />
              <FormHelperText id="outlined-weight-helper-text">
                Weight
              </FormHelperText>
            </FormControl>
          </Stack>
          <Button variant="contained" onClick={calculatePublicationCount}>
            Calculate Count
          </Button>
          {publicationCount !== null && publicationCount !== "" && (
            <PublicationCountPopover
              open={popoverOpen}
              onClose={handlePopoverClose}
              publicationCount={publicationCount}
              onSubmit={handleSubmit}
              onSaveModifiedCount={handleSaveModifiedCount} // Pass the save handler
              keepMounted // Add this to maintain DOM hierarchy
              disableEnforceFocus // Prevent focus trapping
            />
          )}
        </Stack>
      </Box>
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        sx={{ marginTop: "24px" }}
        ClickAwayListenerProps={{ mouseEvent: false }} // Prevent focus issues
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
};

export default PublicationCounter;
