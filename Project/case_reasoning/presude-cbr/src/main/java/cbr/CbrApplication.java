package cbr;

import java.util.Arrays;
import java.util.Collection;

import connector.CsvConnector;
import es.ucm.fdi.gaia.jcolibri.casebase.LinealCaseBase;
import es.ucm.fdi.gaia.jcolibri.cbraplications.StandardCBRApplication;
import es.ucm.fdi.gaia.jcolibri.cbrcore.Attribute;
import es.ucm.fdi.gaia.jcolibri.cbrcore.CBRCase;
import es.ucm.fdi.gaia.jcolibri.cbrcore.CBRCaseBase;
import es.ucm.fdi.gaia.jcolibri.cbrcore.CBRQuery;
import es.ucm.fdi.gaia.jcolibri.cbrcore.Connector;
import es.ucm.fdi.gaia.jcolibri.exception.ExecutionException;
import es.ucm.fdi.gaia.jcolibri.method.retrieve.RetrievalResult;
import es.ucm.fdi.gaia.jcolibri.method.retrieve.NNretrieval.NNConfig;
import es.ucm.fdi.gaia.jcolibri.method.retrieve.NNretrieval.NNScoringMethod;
import es.ucm.fdi.gaia.jcolibri.method.retrieve.NNretrieval.similarity.global.Average;
import es.ucm.fdi.gaia.jcolibri.method.retrieve.NNretrieval.similarity.local.Equal;
import es.ucm.fdi.gaia.jcolibri.method.retrieve.selection.SelectCases;
import model.CaseDescription;
import similarity.IntervalSimilarity;
import similarity.TabularSimilarity;
import similarity.ThresholdSimilarity;

/**
 * Aplikacija za rasudjivanje po slucajevima (CBR) za krivicna djela
 * protiv platnog prometa (Glava 23 KZ CG).
 *
 * Koristimo jCOLIBRI okvir sa KNN pretragom i funkcijama slicnosti
 * modelovanim za 19 kljucnih cinjenica:
 *
 *  1. tipKrivicnogDjela  - TabularSimilarity (falsifikovanje novca vs zloupotreba kartica)
 *  2. clanKZ             - TabularSimilarity (cl. 258, 258/2, 258/4, 260, 260/1, 260/2, 260/3)
 *  3. iznos              - IntervalSimilarity (interval 15000 EUR)
 *  4. ranijeOsudjivan    - TabularSimilarity (da/ne/nepoznat)
 *  5. uslovnaOsuda       - Equal
 *  6. vrstaPresude       - TabularSimilarity (osudjujuca/oslobadjajuca/uslovna)
 *  7. zaposlenost        - TabularSimilarity (zaposlen/nezaposlen/student/penzioner/nepoznat)
 *  8. bracniStatus       - TabularSimilarity (ozenjen/neozenjen/razveden/nepoznat)
 *  9. kaznaUMjesecima    - IntervalSimilarity (interval 60 mjeseci = 5 god)
 * 10. novcanaKazna       - IntervalSimilarity (interval 5000 EUR)
 * 11. obrazovanje        - TabularSimilarity (SSS/VSS/osnovna/pismen/nepoznat)
 * 12. ukupanIznos        - IntervalSimilarity (interval 50000 EUR)
 * 13. brojTransakcija    - IntervalSimilarity (interval 30)
 * 14. brojOkrivljenih    - ThresholdSimilarity (prag 2)
 * 15. brojSvjedoka       - IntervalSimilarity (interval 10)
 * 16. brojDokaza         - IntervalSimilarity (interval 15)
 * 17. priznanje          - Equal (da/ne)
 * 18. pokusaj            - Equal (da/ne)
 * 19. saizvrsilastvo     - Equal (da/ne)
 *
 * Globalna slicnost: prosjek svih lokalnih slicnosti (Average).
 */
public class CbrApplication implements StandardCBRApplication {

    Connector _connector;
    CBRCaseBase _caseBase;
    NNConfig simConfig;

    @Override
    public void configure() throws ExecutionException {
        _connector = new CsvConnector();
        _caseBase = new LinealCaseBase();
        simConfig = new NNConfig();

        // Globalna funkcija slicnosti = prosjek
        simConfig.setDescriptionSimFunction(new Average());

        // ===== 1. Tip krivicnog djela =====
        // Obrazlozenje: Falsifikovanje novca i zloupotreba platnih kartica su
        // razlicita krivicna djela ali oba spadaju u istu glavu (23) KZ.
        // Slicnost je 0.3 jer imaju razlicite elemente bica djela ali istu
        // zasticenu vrijednost (platni promet).
        TabularSimilarity slicnostTipa = new TabularSimilarity(Arrays.asList(
                "falsifikovanje novca",
                "zloupotreba platnih kartica"
        ));
        slicnostTipa.setSimilarity("falsifikovanje novca", "zloupotreba platnih kartica", 0.3);
        simConfig.addMapping(new Attribute("tipKrivicnogDjela", CaseDescription.class), slicnostTipa);

        // ===== 2. Clan Krivicnog zakonika =====
        // Obrazlozenje: Clanovi istog krivicnog djela (npr. razliciti stavovi
        // clana 258) su medjusobno slicniji nego clanovi razlicitih djela.
        // cl. 258 (osnovni) vs cl. 258 st. 2 (nabavljanje) = 0.7
        // cl. 258 vs cl. 258 st. 4 (privilegovani oblik) = 0.5
        // cl. 260 st. 1 vs cl. 260 st. 2 = 0.7
        // cl. 258 vs cl. 260 (razlicita djela) = 0.2
        TabularSimilarity slicnostClana = new TabularSimilarity(Arrays.asList(
                "čl. 258",
                "čl. 258 st. 2",
                "čl. 258 st. 4",
                "čl. 260",
                "čl. 260 st. 1",
                "čl. 260 st. 2",
                "čl. 260 st. 3"
        ));
        // Unutar clana 258 (falsifikovanje novca)
        slicnostClana.setSimilarity("čl. 258", "čl. 258 st. 2", 0.7);
        slicnostClana.setSimilarity("čl. 258", "čl. 258 st. 4", 0.5);
        slicnostClana.setSimilarity("čl. 258 st. 2", "čl. 258 st. 4", 0.4);
        // Unutar clana 260 (zloupotreba platnih kartica)
        slicnostClana.setSimilarity("čl. 260", "čl. 260 st. 1", 0.8);
        slicnostClana.setSimilarity("čl. 260", "čl. 260 st. 2", 0.7);
        slicnostClana.setSimilarity("čl. 260", "čl. 260 st. 3", 0.6);
        slicnostClana.setSimilarity("čl. 260 st. 1", "čl. 260 st. 2", 0.7);
        slicnostClana.setSimilarity("čl. 260 st. 1", "čl. 260 st. 3", 0.5);
        slicnostClana.setSimilarity("čl. 260 st. 2", "čl. 260 st. 3", 0.6);
        // Izmedju clanova 258 i 260 (razlicita krivicna djela iste glave)
        slicnostClana.setSimilarity("čl. 258", "čl. 260", 0.2);
        slicnostClana.setSimilarity("čl. 258", "čl. 260 st. 1", 0.2);
        slicnostClana.setSimilarity("čl. 258", "čl. 260 st. 2", 0.2);
        slicnostClana.setSimilarity("čl. 258", "čl. 260 st. 3", 0.15);
        slicnostClana.setSimilarity("čl. 258 st. 2", "čl. 260", 0.2);
        slicnostClana.setSimilarity("čl. 258 st. 2", "čl. 260 st. 1", 0.2);
        slicnostClana.setSimilarity("čl. 258 st. 2", "čl. 260 st. 2", 0.2);
        slicnostClana.setSimilarity("čl. 258 st. 2", "čl. 260 st. 3", 0.15);
        slicnostClana.setSimilarity("čl. 258 st. 4", "čl. 260", 0.15);
        slicnostClana.setSimilarity("čl. 258 st. 4", "čl. 260 st. 1", 0.15);
        slicnostClana.setSimilarity("čl. 258 st. 4", "čl. 260 st. 2", 0.15);
        slicnostClana.setSimilarity("čl. 258 st. 4", "čl. 260 st. 3", 0.1);
        simConfig.addMapping(new Attribute("clanKZ", CaseDescription.class), slicnostClana);

        // ===== 3. Iznos pribavljene imovinske koristi (EUR) =====
        // Obrazlozenje: Veci iznos = teza kvalifikacija. Interval 15000 EUR
        // jer je to prag za kvalifikovani oblik (cl. 258 st. 3).
        // Razlika od 100 EUR daje slicnost ~0.99, razlika od 7500 EUR = 0.5.
        simConfig.addMapping(new Attribute("iznos", CaseDescription.class),
                new IntervalSimilarity(15000));

        // ===== 4. Ranije osudjivan =====
        // Obrazlozenje: Recidivizam je bitan faktor pri odlucivanju o kazni.
        // "da" vs "ne" = 0.0 (potpuno razlicito jer recidivist dobija vecu kaznu)
        // "nepoznat" vs "da"/"ne" = 0.3 (nedostatak informacije)
        TabularSimilarity slicnostRecidivizma = new TabularSimilarity(Arrays.asList(
                "da", "ne", "nepoznat"
        ));
        slicnostRecidivizma.setSimilarity("da", "ne", 0.0);
        slicnostRecidivizma.setSimilarity("da", "nepoznat", 0.3);
        slicnostRecidivizma.setSimilarity("ne", "nepoznat", 0.3);
        simConfig.addMapping(new Attribute("ranijeOsudjivan", CaseDescription.class), slicnostRecidivizma);

        // ===== 5. Uslovna osuda =====
        // Obrazlozenje: Da li je izrecena uslovna kazna - binarno polje,
        // koristi se Equal (1.0 ako je isto, 0.0 inace).
        simConfig.addMapping(new Attribute("uslovnaOsuda", CaseDescription.class), new Equal());

        // ===== 6. Vrsta presude =====
        // Obrazlozenje: Osudjujuca i uslovna su slicnije (obe znace krivicu)
        // nego oslobadjajuca. Uslovna i osudjujuca = 0.6.
        // Oslobadjajuca vs ostale = 0.1
        TabularSimilarity slicnostPresude = new TabularSimilarity(Arrays.asList(
                "osudjujuca", "uslovna", "oslobadjajuca", "nepoznat"
        ));
        slicnostPresude.setSimilarity("osudjujuca", "uslovna", 0.6);
        slicnostPresude.setSimilarity("osudjujuca", "oslobadjajuca", 0.1);
        slicnostPresude.setSimilarity("uslovna", "oslobadjajuca", 0.1);
        slicnostPresude.setSimilarity("osudjujuca", "nepoznat", 0.2);
        slicnostPresude.setSimilarity("uslovna", "nepoznat", 0.2);
        slicnostPresude.setSimilarity("oslobadjajuca", "nepoznat", 0.2);
        simConfig.addMapping(new Attribute("vrstaPresude", CaseDescription.class), slicnostPresude);

        // ===== 7. Zaposlenost =====
        // Obrazlozenje: Imovno stanje i zaposlenost uticu na odmjeravanje kazne.
        // Nezaposleni i studenti su u slicnoj materijalnoj situaciji (0.6).
        // Zaposlen vs nezaposlen = 0.3 (razlicita imovinska situacija).
        TabularSimilarity slicnostZaposlenosti = new TabularSimilarity(Arrays.asList(
                "zaposlen", "nezaposlen", "student", "penzioner", "nepoznat"
        ));
        slicnostZaposlenosti.setSimilarity("zaposlen", "nezaposlen", 0.3);
        slicnostZaposlenosti.setSimilarity("zaposlen", "student", 0.3);
        slicnostZaposlenosti.setSimilarity("zaposlen", "penzioner", 0.5);
        slicnostZaposlenosti.setSimilarity("nezaposlen", "student", 0.6);
        slicnostZaposlenosti.setSimilarity("nezaposlen", "penzioner", 0.4);
        slicnostZaposlenosti.setSimilarity("student", "penzioner", 0.3);
        slicnostZaposlenosti.setSimilarity("zaposlen", "nepoznat", 0.3);
        slicnostZaposlenosti.setSimilarity("nezaposlen", "nepoznat", 0.3);
        slicnostZaposlenosti.setSimilarity("student", "nepoznat", 0.3);
        slicnostZaposlenosti.setSimilarity("penzioner", "nepoznat", 0.3);
        simConfig.addMapping(new Attribute("zaposlenost", CaseDescription.class), slicnostZaposlenosti);

        // ===== 8. Bracni status =====
        // Obrazlozenje: Moze uticati na odmjeravanje kazne (porodicne prilike).
        // Ozenjen/neozenjen = 0.5 (razlicite prilike ali oboje aktivni)
        // Razveden = medju-stanje
        TabularSimilarity slicnostBracnog = new TabularSimilarity(Arrays.asList(
                "ozenjen", "neozenjen", "razveden", "nepoznat"
        ));
        slicnostBracnog.setSimilarity("ozenjen", "neozenjen", 0.5);
        slicnostBracnog.setSimilarity("ozenjen", "razveden", 0.4);
        slicnostBracnog.setSimilarity("neozenjen", "razveden", 0.6);
        slicnostBracnog.setSimilarity("ozenjen", "nepoznat", 0.3);
        slicnostBracnog.setSimilarity("neozenjen", "nepoznat", 0.3);
        slicnostBracnog.setSimilarity("razveden", "nepoznat", 0.3);
        simConfig.addMapping(new Attribute("bracniStatus", CaseDescription.class), slicnostBracnog);

        // ===== 9. Kazna zatvora u mjesecima =====
        // Obrazlozenje: Trajanje zatvorske kazne. Interval 60 mjeseci (5 god)
        // jer je to maksimum za cl. 260 st. 2. Za cl. 258 ide do 12 god.
        // Razlika od 6 mjeseci daje slicnost ~0.9.
        simConfig.addMapping(new Attribute("kaznaUMjesecima", CaseDescription.class),
                new IntervalSimilarity(60));

        // ===== 10. Novcana kazna (EUR) =====
        // Obrazlozenje: Visina novcane kazne. Interval 5000 EUR pokriva
        // uobicajeni raspon novcanih kazni za ova krivicna djela.
        simConfig.addMapping(new Attribute("novcanaKazna", CaseDescription.class),
                new IntervalSimilarity(5000));

        // ===== 11. Obrazovanje =====
        // Obrazlozenje: Nivo obrazovanja moze uticati na odmjeravanje kazne
        // (olaksavajuca/otezavajuca okolnost). SSS i pismen su slicni (0.6),
        // VSS je distinktivniji. Nepoznat = 0.3 prema svima.
        TabularSimilarity slicnostObrazovanja = new TabularSimilarity(Arrays.asList(
                "SSS", "VSS", "osnovna", "pismen", "nepoznat"
        ));
        slicnostObrazovanja.setSimilarity("SSS", "VSS", 0.4);
        slicnostObrazovanja.setSimilarity("SSS", "osnovna", 0.6);
        slicnostObrazovanja.setSimilarity("SSS", "pismen", 0.6);
        slicnostObrazovanja.setSimilarity("VSS", "osnovna", 0.2);
        slicnostObrazovanja.setSimilarity("VSS", "pismen", 0.3);
        slicnostObrazovanja.setSimilarity("osnovna", "pismen", 0.7);
        slicnostObrazovanja.setSimilarity("SSS", "nepoznat", 0.3);
        slicnostObrazovanja.setSimilarity("VSS", "nepoznat", 0.3);
        slicnostObrazovanja.setSimilarity("osnovna", "nepoznat", 0.3);
        slicnostObrazovanja.setSimilarity("pismen", "nepoznat", 0.3);
        simConfig.addMapping(new Attribute("obrazovanje", CaseDescription.class), slicnostObrazovanja);

        // ===== 12. Ukupan iznos svih transakcija (EUR) =====
        // Obrazlozenje: Ukupna steta je bitan faktor za odmjeravanje kazne.
        // Interval 50000 EUR jer su ukupni iznosi kod karticnih prevara
        // znacajno veci od pojedinacnih transakcija.
        simConfig.addMapping(new Attribute("ukupanIznos", CaseDescription.class),
                new IntervalSimilarity(50000));

        // ===== 13. Broj transakcija =====
        // Obrazlozenje: Vise transakcija = veca upornost = teza kvalifikacija.
        // Interval 30 pokriva raspon (1-30+ transakcija u nasim slucajevima).
        simConfig.addMapping(new Attribute("brojTransakcija", CaseDescription.class),
                new IntervalSimilarity(30));

        // ===== 14. Broj okrivljenih =====
        // Obrazlozenje: Organizovano izvrsenje (vise lica) je otezavajuca okolnost.
        // ThresholdSimilarity(2): slicnost=1 ako razlika <2, inace 0.
        simConfig.addMapping(new Attribute("brojOkrivljenih", CaseDescription.class),
                new ThresholdSimilarity(2));

        // ===== 15. Broj svjedoka =====
        // Obrazlozenje: Vise svjedoka = jaci dokazi. Interval 10.
        simConfig.addMapping(new Attribute("brojSvjedoka", CaseDescription.class),
                new IntervalSimilarity(10));

        // ===== 16. Broj dokaza =====
        // Obrazlozenje: Kolicina dokaznog materijala utice na ishod.
        // Interval 15 pokriva raspon (1-15+ dokaza).
        simConfig.addMapping(new Attribute("brojDokaza", CaseDescription.class),
                new IntervalSimilarity(15));

        // ===== 17. Priznanje krivice =====
        // Obrazlozenje: Priznanje je znacajna olaksavajuca okolnost.
        // Binarno: da/ne. Equal (1.0 ako je isto, 0.0 ako razlicito).
        simConfig.addMapping(new Attribute("priznanje", CaseDescription.class), new Equal());

        // ===== 18. Pokusaj =====
        // Obrazlozenje: Pokusaj krivicnog djela se blaze kaznjava od
        // dovrsenog djela. Binarno: da/ne.
        simConfig.addMapping(new Attribute("pokusaj", CaseDescription.class), new Equal());

        // ===== 19. Saizvrsilastvo =====
        // Obrazlozenje: Zajednicko izvrsenje djela (po prethodnom dogovoru)
        // je otezavajuca okolnost. Binarno: da/ne.
        simConfig.addMapping(new Attribute("saizvrsilastvo", CaseDescription.class), new Equal());
    }

    @Override
    public CBRCaseBase preCycle() throws ExecutionException {
        _caseBase.init(_connector);
        Collection<CBRCase> cases = _caseBase.getCases();
        System.out.println("=== Ucitano " + cases.size() + " slucajeva iz baze ===\n");
        return _caseBase;
    }

    @Override
    public void cycle(CBRQuery query) throws ExecutionException {
        // KNN pretraga - pronalazi najslicnije slucajeve
        Collection<RetrievalResult> eval =
                NNScoringMethod.evaluateSimilarity(_caseBase.getCases(), query, simConfig);

        // Izbor top 5 najslicnijih
        eval = SelectCases.selectTopKRR(eval, 5);

        System.out.println("=== Pronadjeni slicni slucajevi (top 5) ===\n");
        int rank = 1;
        for (RetrievalResult rr : eval) {
            CaseDescription desc = (CaseDescription) rr.get_case().getDescription();
            System.out.printf("  %d. Slicnost: %.2f%%%n", rank, rr.getEval() * 100);
            System.out.printf("     %s%n", desc);
            System.out.printf("     Clan: %s | Presuda: %s | Kazna: %.0f mj | Novcana: %.0f EUR%n%n",
                    desc.getClanKZ(), desc.getVrstaPresude(),
                    desc.getKaznaUMjesecima(), desc.getNovcanaKazna());
            rank++;
        }
    }

    @Override
    public void postCycle() throws ExecutionException {
        // Ovdje se novi slucaj moze sacuvati u bazu (CSV)
    }

    /**
     * Primjer pokretanja CBR sistema sa novim slucajem.
     */
    public static void main(String[] args) {
        StandardCBRApplication cbr = new CbrApplication();
        try {
            cbr.configure();
            cbr.preCycle();

            // ===== Novi slucaj za rasudjivanje =====
            CBRQuery query = new CBRQuery();
            CaseDescription noviSlucaj = new CaseDescription();

            // Primer 1: Falsifikovanje novca - okrivljeni stavio u opticaj laznu
            // novcanicu od 50 EUR, ranije neosudjivan, nezaposlen, SSS obrazovanje
            noviSlucaj.setTipKrivicnogDjela("falsifikovanje novca");
            noviSlucaj.setClanKZ("čl. 258");
            noviSlucaj.setIznos(50.0);            // 50 EUR lazna novcanica
            noviSlucaj.setRanijeOsudjivan("ne");
            noviSlucaj.setUslovnaOsuda("Da");
            noviSlucaj.setVrstaPresude("uslovna");
            noviSlucaj.setZaposlenost("nezaposlen");
            noviSlucaj.setBracniStatus("neozenjen");
            noviSlucaj.setKaznaUMjesecima(0);     // nepoznato - trazimo predlog
            noviSlucaj.setNovcanaKazna(0);         // nepoznato - trazimo predlog
            noviSlucaj.setObrazovanje("SSS");
            noviSlucaj.setUkupanIznos(50.0);      // samo jedna novcanica
            noviSlucaj.setBrojTransakcija(1);
            noviSlucaj.setBrojOkrivljenih(1);
            noviSlucaj.setBrojSvjedoka(1);
            noviSlucaj.setBrojDokaza(3);
            noviSlucaj.setPriznanje("ne");
            noviSlucaj.setPokusaj("ne");
            noviSlucaj.setSaizvrsilastvo("ne");

            query.setDescription(noviSlucaj);

            System.out.println("=== Novi slucaj za rasudjivanje ===");
            System.out.println(noviSlucaj);
            System.out.println();

            cbr.cycle(query);

            // Primer 2: Zloupotreba platne kartice - koristio tudju karticu,
            // podigao 300 EUR, zaposlen, ranije neosudjivan, vise transakcija
            System.out.println("\n========================================\n");

            CBRQuery query2 = new CBRQuery();
            CaseDescription noviSlucaj2 = new CaseDescription();
            noviSlucaj2.setTipKrivicnogDjela("zloupotreba platnih kartica");
            noviSlucaj2.setClanKZ("čl. 260 st. 2");
            noviSlucaj2.setIznos(300.0);
            noviSlucaj2.setRanijeOsudjivan("ne");
            noviSlucaj2.setUslovnaOsuda("Da");
            noviSlucaj2.setVrstaPresude("uslovna");
            noviSlucaj2.setZaposlenost("zaposlen");
            noviSlucaj2.setBracniStatus("ozenjen");
            noviSlucaj2.setKaznaUMjesecima(0);
            noviSlucaj2.setNovcanaKazna(0);
            noviSlucaj2.setObrazovanje("SSS");
            noviSlucaj2.setUkupanIznos(1500.0);    // ukupno 5 transakcija
            noviSlucaj2.setBrojTransakcija(5);
            noviSlucaj2.setBrojOkrivljenih(1);
            noviSlucaj2.setBrojSvjedoka(2);
            noviSlucaj2.setBrojDokaza(5);
            noviSlucaj2.setPriznanje("da");          // priznao krivicu
            noviSlucaj2.setPokusaj("ne");
            noviSlucaj2.setSaizvrsilastvo("ne");

            query2.setDescription(noviSlucaj2);

            System.out.println("=== Novi slucaj za rasudjivanje ===");
            System.out.println(noviSlucaj2);
            System.out.println();

            cbr.cycle(query2);

            cbr.postCycle();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
