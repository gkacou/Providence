CREATE OR REPLACE VIEW public.v_cotisation_non_liberee
AS SELECT c.id,
    c.reunion_id,
    c.membre_id,
    c.montant_social,
    c.social_libere,
    c.montant_mission,
    c.mission_libere,
    (not c.social_libere)::int * c.montant_social - coalesce(s.affecte_social, 0) AS reste_cotis_social,
    (not c.mission_libere)::int * c.montant_mission - coalesce(m.affecte_mission, 0) AS reste_cotis_mission
FROM blog_cotisation c
LEFT JOIN ( SELECT a.cotisation_id,
        sum(a.somme) AS affecte_social
        FROM blog_affectationnonlibere a
            JOIN blog_cas c_1 ON a.cas_id = c_1.id
        WHERE c_1.classification::text = 'S'::text
        GROUP BY a.cotisation_id) s ON s.cotisation_id = c.id
LEFT JOIN ( SELECT a.cotisation_id,
        sum(a.somme) AS affecte_mission
        FROM blog_affectationnonlibere a
            JOIN blog_cas c_1 ON a.cas_id = c_1.id
        WHERE c_1.classification::text = 'M'::text
        GROUP BY a.cotisation_id) m ON m.cotisation_id = c.id
WHERE NOT (c.mission_libere AND c.social_libere);