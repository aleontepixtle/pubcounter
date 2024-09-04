import React, { useState, useEffect } from "react";
import TextField from "@mui/material/TextField";
import Autocomplete from "@mui/material/Autocomplete";
import TravelExploreRoundedIcon from "@mui/icons-material/TravelExploreRounded";
import { InputAdornment } from "@mui/material";
import { database, ref, get } from "../PublicationSearch/firebase/firebase";

const PublicationSearch = ({ onPublicationSelect }) => {
  const [publicationNameOptions, setPublicationNameOptions] = useState([]);
  const [publications, setPublications] = useState([]);

  useEffect(() => {
    const fetchPublications = async () => {
      try {
        const publicationsRef = ref(database);
        const snapshot = await get(publicationsRef);
        if (snapshot.exists()) {
          const publicationsData = snapshot.val();
          const publicationNames = Object.keys(publicationsData).map(
            (key) => `${publicationsData[key].name} (${publicationsData[key].jwId})`
          );
          setPublications(publicationsData);
          setPublicationNameOptions(publicationNames);
        } else {
          console.error("No data available");
        }
      } catch (error) {
        console.error("Error fetching publications from database:", error);
      }
    };

    fetchPublications();
  }, []);

  const handleSelectionChange = (event, value) => {
    const selected = Object.values(publications).find(
      (pub) => `${pub.name} (${pub.jwId})` === value
    );
    // If no publication is selected (value is null), pass null to reset the fields
    onPublicationSelect(selected || null);
  };

  return (
    <Autocomplete
      options={publicationNameOptions}
      onChange={handleSelectionChange}
      renderInput={(params) => (
        <TextField
          {...params}
          label="Search For Publication"
          sx={{ m: 0, width: "35ch" }}
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
        const filtered = options.filter((option) =>
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
