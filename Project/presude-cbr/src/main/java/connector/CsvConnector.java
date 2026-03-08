package connector;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URL;
import java.util.Collection;
import java.util.LinkedList;

import es.ucm.fdi.gaia.jcolibri.cbrcore.CBRCase;
import es.ucm.fdi.gaia.jcolibri.cbrcore.CaseBaseFilter;
import es.ucm.fdi.gaia.jcolibri.cbrcore.Connector;
import es.ucm.fdi.gaia.jcolibri.exception.InitializingException;
import model.CaseDescription;

/**
 * Cita slucajeve iz CSV fajla (presude.csv) koji je generisan
 * ekstrahovanjem podataka iz Akomanotoso XML dokumenata.
 *
 * Format CSV-a (separator: ;):
 * id;sud;brojPredmeta;tipKrivicnogDjela;clanKZ;iznos;ranijeOsudjivan;
 * uslovnaOsuda;vrstaPresude;zaposlenost;bracniStatus;kaznaUMjesecima;novcanaKazna;
 * obrazovanje;ukupanIznos;brojTransakcija;brojOkrivljenih;brojSvjedoka;brojDokaza;
 * priznanje;pokusaj;saizvrsilastvo
 */
public class CsvConnector implements Connector {

    @Override
    public Collection<CBRCase> retrieveAllCases() {
        LinkedList<CBRCase> cases = new LinkedList<>();

        try (BufferedReader br = new BufferedReader(
                new InputStreamReader(getClass().getResourceAsStream("/presude.csv"), "UTF-8"))) {

            String line;
            while ((line = br.readLine()) != null) {
                // Skip comments and empty lines
                if (line.startsWith("#") || line.trim().isEmpty())
                    continue;

                String[] v = line.split(";", -1);
                if (v.length < 22)
                    continue;

                CaseDescription desc = new CaseDescription();
                desc.setId(Integer.parseInt(v[0].trim()));
                desc.setSud(v[1].trim());
                desc.setBrojPredmeta(v[2].trim());
                desc.setTipKrivicnogDjela(v[3].trim());
                desc.setClanKZ(v[4].trim());
                desc.setIznos(parseDouble(v[5]));
                desc.setRanijeOsudjivan(v[6].trim());
                desc.setUslovnaOsuda(v[7].trim());
                desc.setVrstaPresude(v[8].trim());
                desc.setZaposlenost(v[9].trim());
                desc.setBracniStatus(v[10].trim());
                desc.setKaznaUMjesecima(parseDouble(v[11]));
                desc.setNovcanaKazna(parseDouble(v[12]));
                desc.setObrazovanje(v[13].trim());
                desc.setUkupanIznos(parseDouble(v[14]));
                desc.setBrojTransakcija(parseInt(v[15]));
                desc.setBrojOkrivljenih(parseInt(v[16]));
                desc.setBrojSvjedoka(parseInt(v[17]));
                desc.setBrojDokaza(parseInt(v[18]));
                desc.setPriznanje(v[19].trim());
                desc.setPokusaj(v[20].trim());
                desc.setSaizvrsilastvo(v[21].trim());

                CBRCase cbrCase = new CBRCase();
                cbrCase.setDescription(desc);
                cases.add(cbrCase);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        return cases;
    }

    private double parseDouble(String s) {
        try {
            return Double.parseDouble(s.trim());
        } catch (NumberFormatException e) {
            return 0.0;
        }
    }

    private int parseInt(String s) {
        try {
            return Integer.parseInt(s.trim());
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    @Override
    public Collection<CBRCase> retrieveSomeCases(CaseBaseFilter filter) {
        return null;
    }

    @Override
    public void storeCases(Collection<CBRCase> cases) {
    }

    @Override
    public void close() {
    }

    @Override
    public void deleteCases(Collection<CBRCase> cases) {
    }

    @Override
    public void initFromXMLfile(URL url) throws InitializingException {
    }
}
