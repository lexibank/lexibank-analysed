SELECT
    Language_Name,
    Language_ID,
    Glottocode,
    Family,
    Latitude,
    Longitude
FROM
    forms_with_cc
WHERE
    forms_with_cc.Consonant_Classes = ? AND
    forms_with_cc.Concepticon_Gloss = ?
GROUP BY
    Language_Name,
    Language_ID,
    Glottocode
;