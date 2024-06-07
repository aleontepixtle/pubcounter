import React, { useState, useEffect } from "react";
import TextField from "@mui/material/TextField";
import Autocomplete from "@mui/material/Autocomplete";
import TravelExploreRoundedIcon from "@mui/icons-material/TravelExploreRounded";
import { InputAdornment } from "@mui/material";
import axios from "axios";

const PublicationSearch = () => {
  const [publicationNameOptions, setPublicationNameOptions] = useState([]);
  const filePath = "GeneratedInventories/Inventory_2024-06-06.json"; // TODO: change this to be the most recent inventory file
  
  useEffect(() => {
    const fetchPublications = async () => {
      try {
        const response = await axios.get(filePath);
        const publications = response.data;
        const publicationNames = publications.map(pub => `${pub.name} (${pub.jwId})`);
        console.log('Publications Fetched Successfully!');
        setPublicationNameOptions(publicationNames);
      } catch (error) {
        console.error("Error fetching publications:", error);
      }
    };

    fetchPublications();
  }, []);
  
  return (
    <Autocomplete
      options={publicationNameOptions}
      renderInput={(params) => (
        <TextField
          {...params}
          label="Search For Publication"
          sx={{ m: 0, width: '35ch' }}
          InputProps={{
            ...params.InputProps,
            startAdornment: (
              <InputAdornment position="start">
                <TravelExploreRoundedIcon />
              </InputAdornment>
            ),
          }}
        />
      )}
      filterOptions={(options, params) => {
        const filtered = options.filter(
          (option) =>
            option.toLowerCase().includes(params.inputValue.toLowerCase())
        );

        if (params.inputValue.length >= 2) {
          return filtered;
        }
        return options;
      }}
    />
  );
};

export default PublicationSearch;
