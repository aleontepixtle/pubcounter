import React, { useState, useEffect } from "react";
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
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import PublicationCountPopover from "../PublicationCountPopover/PublicationCountPopover";
import PublicationSearch from "../PublicationSearch/PublicationSearch";
import { database, ref, set, get } from "../PublicationSearch/firebase/firebase";
import { createTheme, ThemeProvider } from "@mui/material/styles";

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
  const [publicationBatches, setPublicationBatches] = useState([]);
  const [totalPublications, setTotalPublications] = useState(0);
  const [isAddingMore, setIsAddingMore] = useState(false);
  const [warningOpen, setWarningOpen] = useState(false);

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
    resetTotalPublications(); // Reset total publications when changing unit of measure
  };

  const handleCountChange = (e) => {
    setSelectedCount(parseInt(e.target.value));
    resetTotalPublications(); // Reset total publications when changing unit of measure count
  };

  const calculatePublicationCount = () => {
    if (!unitOfMeasureWeight || !totalWeightOfBatch || !selectedUnitOfMeasureCount) {
      alert("Please enter valid values for all fields.");
      return;
    }

    const calculatedCount =
      (totalWeightOfBatch / unitOfMeasureWeight) * selectedUnitOfMeasureCount;
    setPublicationCount(Math.round(calculatedCount));
    setPopoverOpen(true);  // Open the popover after setting the count
    if (!isAddingMore) {
      setTotalPublications(Math.round(calculatedCount)); // Set total publications to calculated count if not adding more
    }
  };

  const togglePopover = () => {
    if (!isAddingMore && totalPublications > 0 && publicationBatches.length > 0) {
      setWarningOpen(true);
    } else {
      setPopoverOpen(!popoverOpen);
    }
  };

  const handleAddMore = () => {
    if (publicationCount) {
      setTotalPublications((prevTotal) => prevTotal + publicationCount); // Add to total publications
      setPublicationBatches([...publicationBatches, publicationCount]);
      setPopoverOpen(false);  // Close the popover after adding
      setIsAddingMore(true);  // Set adding more state to true
    }
  };

  const handleDoneAdding = () => {
    setIsAddingMore(false);  // Set adding more state to false
    setPopoverOpen(true);  // Open the popover after done adding
  };

  const handleSubmit = async () => {
    if (selectedPublication) {
      const publicationsRef = ref(database);
      const snapshot = await get(publicationsRef);
      if (snapshot.exists()) {
        const publicationsArray = snapshot.val();

        const publicationIndex = publicationsArray.findIndex(
          (pub) => pub.jwId === selectedPublication.jwId
        );
        if (publicationIndex !== -1) {
          publicationsArray[publicationIndex].quantity = totalPublications;

          await set(publicationsRef, publicationsArray);
          alert("Publication quantity updated successfully!");
        } else {
          alert("Publication not found.");
        }
      } else {
        alert("No data available.");
      }

      setPublicationBatches([]);
      setTotalPublications(0);
      setPopoverOpen(false);  // Close the popover after submission
      setIsAddingMore(false);  // Reset adding more state
    } else {
      alert("Please select a publication.");
    }
  };

  const handlePublicationSelect = (publication) => {
    setSelectedPublication(publication);
    reset(); // Reset state when a new publication is selected
  };

  const handleEditTotal = (value) => {
    setTotalPublications(value === "" ? 0 : parseInt(value, 10));
  };

  const reset = () => {
    setUnitOfMeasureWeight(0);
    setTotalWeightOfBatch(0);
    setSelectedCount(1);
    setPublicationCount(null);
    setPublicationBatches([]);
    setTotalPublications(0);
    setPopoverOpen(false);
    setIsAddingMore(false); // Reset adding more state
  };

  const resetTotalPublications = () => {
    setTotalPublications(0); // Reset total publications
  };

  const handleWarningClose = () => {
    setWarningOpen(false);
  };

  const handleWarningAccept = () => {
    setWarningOpen(false);
    setPopoverOpen(false); // Close the popover
    reset();
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
            <PublicationSearch onPublicationSelect={handlePublicationSelect} disabled={isAddingMore} />
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
                <FormControlLabel value="1" control={<Radio />} label="1" disabled={isAddingMore} />
                <FormControlLabel value="2" control={<Radio />} label="2" disabled={isAddingMore} />
                <FormControlLabel value="5" control={<Radio />} label="5" disabled={isAddingMore} />
                <FormControlLabel value="10" control={<Radio />} label="10" disabled={isAddingMore} />
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
                sx={{
                  '& .MuiOutlinedInput-root': {
                    '& fieldset': {
                      borderColor: 'green', // Green border color
                    },
                  },
                }}
                disabled={isAddingMore} // Disable if adding more
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
                sx={{
                  '& .MuiOutlinedInput-root': {
                    '& fieldset': {
                      borderColor: 'green', // Green border color
                    },
                  },
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
        </Stack>
      </Box>
      {popoverOpen && (
        <PublicationCountPopover
          open={popoverOpen}
          onClose={togglePopover}
          publicationCount={publicationCount}
          onSubmit={handleSubmit}
          onAddMore={handleAddMore}
          onDoneAdding={handleDoneAdding} // New prop for Done Adding button
          totalPublications={totalPublications}
          onEditTotal={handleEditTotal}
          isPublicationSelected={!!selectedPublication} // Pass the selected publication state
          isAddingMore={isAddingMore} // Pass the isAddingMore state
        />
      )}
      <Dialog
        open={warningOpen}
        onClose={handleWarningClose}
      >
        <DialogTitle>Warning</DialogTitle>
        <DialogContent>
          <DialogContentText>
            You have not submitted your count totals. If you close the popover, your counts will be lost.
            Would you like to keep counting or reset the counts?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleWarningClose} color="primary">
            Keep Counting
          </Button>
          <Button onClick={handleWarningAccept} color="primary" autoFocus>
            Accept & Close
          </Button>
        </DialogActions>
      </Dialog>
    </ThemeProvider>
  );
};

export default PublicationCounter;
