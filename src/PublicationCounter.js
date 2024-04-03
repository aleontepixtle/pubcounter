import React, { useState } from "react";
import "./PublicationCounter.css";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Divider from '@mui/material/Divider';

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
        <label>
          Unit of Measure Weight:
          <input
            type="number"
            value={unitOfMeasureWeight}
            onChange={handleUnitOfMeasureWeightChange}
          />
        </label>
        <label>
          Total Weight of Batch:
          <input
            type="number"
            value={totalWeightOfBatch}
            onChange={handleInputChange}
          />
        </label>
        <label>
          Count in Unit of Measure:
          <input
            type="number"
            value={countInUnitOfMeasure}
            onChange={(e) => setCountInUnitOfMeasure(e.target.value)}
          />
        </label>
        <Button variant="contained" onClick={calculatePublicationCount}>
          Calculate Publication Count
        </Button>
        {publicationCount > 0 && <p>Publication Count: {publicationCount}</p>}
      </Stack>
    </div>
  );
};

export default PublicationCounter;
