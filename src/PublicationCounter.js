import React, { useState } from "react";
import "./PublicationCounter.css";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Divider from "@mui/material/Divider";
import OutlinedInput from "@mui/material/OutlinedInput";
import InputAdornment from "@mui/material/InputAdornment";
import FormHelperText from "@mui/material/FormHelperText";
import FormControl from "@mui/material/FormControl";
import Typography from "@mui/material/Typography";

const PublicationCounter = () => {
  const [unitOfMeasureWeight, setUnitOfMeasureWeight] = useState(0);
  const [totalWeightOfBatch, setTotalWeightOfBatch] = useState(0);
  const [countInUnitOfMeasure, setCountInUnitOfMeasure] = useState(0);
  const [publicationCount, setPublicationCount] = useState(0);

  const handleInputChange = (e) => {
    const { value } = e.target;
    setTotalWeightOfBatch(value);
  };

  const handleUnitOfMeasureWeightChange = (e) => {
    const { value } = e.target;
    setUnitOfMeasureWeight(value);
  };

  const calculatePublicationCount = () => {
    // Ensure all inputs are valid numbers
    if (!unitOfMeasureWeight || !totalWeightOfBatch || !countInUnitOfMeasure) {
      alert("Please enter valid values for all fields.");
      return;
    }

    // Calculate the publication count
    const calculatedCount =
      totalWeightOfBatch / (unitOfMeasureWeight * countInUnitOfMeasure);
    setPublicationCount(calculatedCount);
  };

  return (
    <div>
      <Stack
        direction="column"
        divider={<Divider orientation="vertical" flexItem />}
        spacing={2}
        justifyContent="center"
        alignItems="center"
      >
        <h1>Publication Counter</h1>
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
              }}
            />
            <FormHelperText id="outlined-weight-helper-text">
              Weight
            </FormHelperText>
          </FormControl>
        </Stack>
        <Stack direction="row" spacing={2}>
          <Typography variant="overline" display="block" gutterBottom>
            Enter Count in Unit of Measure
          </Typography>
          <FormControl sx={{ m: 0, width: "13ch" }} variant="outlined">
            <OutlinedInput
              id="outlined-adornment-weight"
              type="number"
              size="small"
              value={countInUnitOfMeasure}
              onChange={(e) => setCountInUnitOfMeasure(e.target.value)}
              endAdornment={<InputAdornment position="end">g</InputAdornment>}
              aria-describedby="outlined-weight-helper-text"
              inputProps={{
                "aria-label": "count",
              }}
            />
            <FormHelperText id="outlined-weight-helper-text">
              Weight
            </FormHelperText>
          </FormControl>
        </Stack>
        <Button variant="contained" onClick={calculatePublicationCount}>
          Calculate Publication Count
        </Button>
        {publicationCount > 0 && <p>Publication Count: {publicationCount.toFixed(2)}</p>}
      </Stack>
    </div>
  );
};

export default PublicationCounter;
