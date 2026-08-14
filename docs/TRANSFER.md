# Transferència entre instàncies

Tutopy exporta agregats d'alumnes en contenidors xifrats amb extensió `.tutopy`.
El format és per a intercanvi de dades; no és una còpia directa de la base
SQLite.

## Format 1

El contingut xifrat és un ZIP que conté `manifest.json`, `data.json`,
`checksums.json` i, quan correspon,
fitxers sota `documents/<uuid-alumne>/`. El manifest identifica el format,
la versió, l'aplicació d'origen, la data UTC, l'abast i el nombre d'alumnes.

Els IDs SQLite no surten de la instància. Els alumnes es relacionen per UUID,
les categories pel nom normalitzat i els cursos per `YYYY-YYYY`. SHA-256 protegeix
cada document contra corrupció o manipulació accidental.

## Conflictes

Quan l'UUID ja existeix, cal escollir una acció:

- **Conservar local:** omet completament l'alumne del paquet.
- **Substituir:** reemplaça l'agregat local complet dins una transacció.
- **Importar com a nou:** conserva el local i genera un UUID per a la còpia.

La substitució és idempotent. No es fa fusió registre a registre en el format 1.

## Xifrat, seguretat i atomicitat

Tot el contingut es protegeix amb AES-256-GCM, que proporciona confidencialitat
i detecta qualsevol manipulació. La clau es deriva de la contrasenya amb Scrypt
i una sal aleatòria; cada exportació utilitza també un nonce aleatori. La
contrasenya i la clau derivada no s'emmagatzemen. La contrasenya ha de tenir un
mínim de vuit caràcters.

Abans de mostrar la previsualització es validen extensió, mida comprimida i
descomprimida, quantitat de membres, rutes, fitxers permesos, JSON, versió,
UUID i hashes. L'extracció usa un directori temporal.

La persistència s'executa en una transacció SQLite. Els fitxers nous es registren
individualment per poder-los eliminar si hi ha rollback. En una substitució, els
fitxers antics només s'eliminen després del commit correcte.

Una contrasenya incorrecta i un paquet manipulat produeixen deliberadament el
mateix error, perquè no es pot distingir de manera segura entre ambdós casos.
Cal custodiar la contrasenya separadament del paquet i usar-ne una de robusta.

## Errors visibles

La interfície diferencia els errors de contrasenya o integritat, format no
compatible, estructura interna invàlida, límits de mida, dades inconsistents i
errors del sistema de fitxers. Els errors inesperats mostren el tipus d'error i
remeten al registre tècnic, on es conserva el detall per al diagnòstic sense
presentar-lo directament a l'usuari.
