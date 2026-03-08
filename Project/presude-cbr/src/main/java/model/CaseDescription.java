package model;

import es.ucm.fdi.gaia.jcolibri.cbrcore.Attribute;
import es.ucm.fdi.gaia.jcolibri.cbrcore.CaseComponent;

/**
 * Opisuje kljucne cinjenice jednog slucaja iz oblasti krivicnih djela
 * protiv platnog prometa (Glava 23 KZ CG).
 *
 * Atributi (19 kljucnih cinjenica + identifikatori):
 *  1. tipKrivicnogDjela  - vrsta krivicnog djela
 *  2. clanKZ             - clan Krivicnog zakonika
 *  3. iznos              - max iznos pojedinacne transakcije (EUR)
 *  4. ranijeOsudjivan    - da li je okrivljeni ranije osudjivan
 *  5. uslovnaOsuda       - da li je izrecena uslovna osuda
 *  6. vrstaPresude       - tip presude (osudjujuca/oslobadjajuca/uslovna)
 *  7. zaposlenost        - radni status okrivljenog
 *  8. bracniStatus       - bracni status okrivljenog
 *  9. kaznaUMjesecima    - izrecena kazna u mjesecima
 * 10. novcanaKazna       - novcana kazna u EUR
 * 11. obrazovanje        - nivo obrazovanja (SSS/VSS/osnovna/pismen/nepoznat)
 * 12. ukupanIznos        - ukupan zbir svih iznosa (EUR)
 * 13. brojTransakcija    - broj pojedinacnih transakcija
 * 14. brojOkrivljenih    - broj okrivljenih lica u predmetu
 * 15. brojSvjedoka       - broj svjedoka
 * 16. brojDokaza         - broj dokaznih sredstava
 * 17. priznanje          - da li je okrivljeni priznao krivicu
 * 18. pokusaj            - da li je djelo ostalo u pokusaju
 * 19. saizvrsilastvo     - da li postoji saizvrsilastvo/saučesništvo
 */
public class CaseDescription implements CaseComponent {

    private int id;
    private String sud;
    private String brojPredmeta;
    private String tipKrivicnogDjela;
    private String clanKZ;
    private double iznos;
    private String ranijeOsudjivan;
    private String uslovnaOsuda;
    private String vrstaPresude;
    private String zaposlenost;
    private String bracniStatus;
    private double kaznaUMjesecima;
    private double novcanaKazna;
    private String obrazovanje;
    private double ukupanIznos;
    private int brojTransakcija;
    private int brojOkrivljenih;
    private int brojSvjedoka;
    private int brojDokaza;
    private String priznanje;
    private String pokusaj;
    private String saizvrsilastvo;

    // ---- Getteri i setteri ----

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getSud() { return sud; }
    public void setSud(String sud) { this.sud = sud; }

    public String getBrojPredmeta() { return brojPredmeta; }
    public void setBrojPredmeta(String brojPredmeta) { this.brojPredmeta = brojPredmeta; }

    public String getTipKrivicnogDjela() { return tipKrivicnogDjela; }
    public void setTipKrivicnogDjela(String tipKrivicnogDjela) { this.tipKrivicnogDjela = tipKrivicnogDjela; }

    public String getClanKZ() { return clanKZ; }
    public void setClanKZ(String clanKZ) { this.clanKZ = clanKZ; }

    public double getIznos() { return iznos; }
    public void setIznos(double iznos) { this.iznos = iznos; }

    public String getRanijeOsudjivan() { return ranijeOsudjivan; }
    public void setRanijeOsudjivan(String ranijeOsudjivan) { this.ranijeOsudjivan = ranijeOsudjivan; }

    public String getUslovnaOsuda() { return uslovnaOsuda; }
    public void setUslovnaOsuda(String uslovnaOsuda) { this.uslovnaOsuda = uslovnaOsuda; }

    public String getVrstaPresude() { return vrstaPresude; }
    public void setVrstaPresude(String vrstaPresude) { this.vrstaPresude = vrstaPresude; }

    public String getZaposlenost() { return zaposlenost; }
    public void setZaposlenost(String zaposlenost) { this.zaposlenost = zaposlenost; }

    public String getBracniStatus() { return bracniStatus; }
    public void setBracniStatus(String bracniStatus) { this.bracniStatus = bracniStatus; }

    public double getKaznaUMjesecima() { return kaznaUMjesecima; }
    public void setKaznaUMjesecima(double kaznaUMjesecima) { this.kaznaUMjesecima = kaznaUMjesecima; }

    public double getNovcanaKazna() { return novcanaKazna; }
    public void setNovcanaKazna(double novcanaKazna) { this.novcanaKazna = novcanaKazna; }

    public String getObrazovanje() { return obrazovanje; }
    public void setObrazovanje(String obrazovanje) { this.obrazovanje = obrazovanje; }

    public double getUkupanIznos() { return ukupanIznos; }
    public void setUkupanIznos(double ukupanIznos) { this.ukupanIznos = ukupanIznos; }

    public int getBrojTransakcija() { return brojTransakcija; }
    public void setBrojTransakcija(int brojTransakcija) { this.brojTransakcija = brojTransakcija; }

    public int getBrojOkrivljenih() { return brojOkrivljenih; }
    public void setBrojOkrivljenih(int brojOkrivljenih) { this.brojOkrivljenih = brojOkrivljenih; }

    public int getBrojSvjedoka() { return brojSvjedoka; }
    public void setBrojSvjedoka(int brojSvjedoka) { this.brojSvjedoka = brojSvjedoka; }

    public int getBrojDokaza() { return brojDokaza; }
    public void setBrojDokaza(int brojDokaza) { this.brojDokaza = brojDokaza; }

    public String getPriznanje() { return priznanje; }
    public void setPriznanje(String priznanje) { this.priznanje = priznanje; }

    public String getPokusaj() { return pokusaj; }
    public void setPokusaj(String pokusaj) { this.pokusaj = pokusaj; }

    public String getSaizvrsilastvo() { return saizvrsilastvo; }
    public void setSaizvrsilastvo(String saizvrsilastvo) { this.saizvrsilastvo = saizvrsilastvo; }

    @Override
    public String toString() {
        return "Slucaj [id=" + id
                + ", sud=" + sud
                + ", br=" + brojPredmeta
                + ", tip=" + tipKrivicnogDjela
                + ", clan=" + clanKZ
                + ", iznos=" + iznos + "€"
                + ", ukupanIznos=" + ukupanIznos + "€"
                + ", ranijeOsudj=" + ranijeOsudjivan
                + ", uslovna=" + uslovnaOsuda
                + ", presuda=" + vrstaPresude
                + ", zaposlenost=" + zaposlenost
                + ", bracniStatus=" + bracniStatus
                + ", obrazovanje=" + obrazovanje
                + ", kazna=" + kaznaUMjesecima + "mj"
                + ", novcanaKazna=" + novcanaKazna + "€"
                + ", brojTransakcija=" + brojTransakcija
                + ", brojOkrivljenih=" + brojOkrivljenih
                + ", brojSvjedoka=" + brojSvjedoka
                + ", brojDokaza=" + brojDokaza
                + ", priznanje=" + priznanje
                + ", pokusaj=" + pokusaj
                + ", saizvrsilastvo=" + saizvrsilastvo
                + "]";
    }

    @Override
    public Attribute getIdAttribute() {
        return new Attribute("id", this.getClass());
    }
}
