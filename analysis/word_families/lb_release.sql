SELECT 
    COUNT(DISTINCT(p.concepticon_gloss)) AS Count,
    l.cldf_name AS Doculect,
    l.cldf_glottocode AS Glottocode,
    l.cldf_longitude AS Longitude,
    l.cldf_latitude AS Latitude,
    l.family AS Family
FROM 
    LanguageTable AS l,
    FormTable AS f,
    ParameterTable AS p
WHERE
    f.cldf_parameterReference = p.cldf_id
        AND
    f.cldf_languageReference = l.cldf_id
GROUP BY 
    l.cldf_glottocode
ORDER BY 
    Family, Doculect;
