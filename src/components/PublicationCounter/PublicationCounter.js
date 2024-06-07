import React, { useState } from "react";
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

const PublicationCounter = () => {
  const [unitOfMeasureWeight, setUnitOfMeasureWeight] = useState(0);
  const [totalWeightOfBatch, setTotalWeightOfBatch] = useState(0);
  const [selectedUnitOfMeasureCount, setSelectedCount] = useState(1);
  const [publicationCount, setPublicationCount] = useState(null);
  const [popoverOpen, setPopoverOpen] = useState(false);

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
      alert("Please enter valid values for all fields.");
      return;
    }

    const calculatedCount =
      (totalWeightOfBatch / unitOfMeasureWeight) * selectedUnitOfMeasureCount;
    setPublicationCount(Math.round(calculatedCount));
    togglePopover();
  };

  const togglePopover = () => {
    setPopoverOpen(!popoverOpen);
  };

  return (
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
          <ScaleIcon></ScaleIcon>
          <PublicationSearch></PublicationSearch>
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
            onClose={togglePopover}
            publicationCount={publicationCount}
          />
        )}
      </Stack>
    </Box>
  );
};

export default PublicationCounter;
