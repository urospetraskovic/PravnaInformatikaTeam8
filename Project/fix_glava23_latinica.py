#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# Path to the HTML file
html_file = r"c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\src\web\public\index.html"

# Read the HTML file
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# New articles section in pure Latinica (copied from glava 23.txt)
new_articles = '''          <!-- Član 258 - Falsifikovanje novca -->
          <div class="article" id="258">
            <div class="article-number">Član 258 - Falsifikovanje novca</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko napravi lažan novac u namjeri da ga stavi u opticaj kao pravi ili ko u istoj namjeri preinači pravi novac, kazniće se zatvorom od dvije do dvanaest godina.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Ko pribavlja, drži ili prenosi lažan novac u namjeri da ga stavi u opticaj kao pravi ili ko lažan novac stavlja u opticaj, kazniće se zatvorom od dvije do deset godina.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Ako je djelom iz st. 1 i 2 ovog člana napravljen, preinačen, stavljen u promet ili pribavljen lažan novac u iznosu koji prelazi petnaest hiljada eura, odnosno odgovarajući iznos u stranom novcu, učinilac će se kazniti zatvorom od pet do petnaest godina.
              </div>
              <div class="paragraph">
                <strong>(4)</strong> Ko lažan novac koji je primio kao pravi, pa saznavši da je lažan, stavi u opticaj ili ko zna da je načinjen lažan novac ili da je lažan novac stavljen u opticaj, pa to ne prijavi, kazniće se novčanom kaznom ili zatvorom do jedne godine.
              </div>
              <div class="paragraph">
                <strong>(5)</strong> Lažan novac oduzeće se.
              </div>
              <div class="paragraph">
                <strong>(6)</strong> Lažnim novcem, u smislu ovog krivičnog djela, smatra se i novac izrađen na način i od materijala kao pravi novac, suprotno propisima kojima se uređuje izrada novca.
              </div>
            </div>
          </div>

          <!-- Član 259 - Falsifikovanje hartija od vrijednosti -->
          <div class="article" id="259">
            <div class="article-number">Član 259 - Falsifikovanje hartija od vrijednosti</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko napravi lažne hartije od vrijednosti ili preinači prave hartije od vrijednosti u namjeri da ih upotrijebi kao prave ili da ih drugom da na upotrebu ili ko takve lažne hartije upotrijebi kao prave ili ih u toj namjeri pribavi, kazniće se zatvorom od jedne do pet godina.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Ako ukupan iznos na koji glase falsifikovane hartije od vrijednosti iz stava 1 ovog člana prelazi tri hiljade eura, učinilac će se kazniti zatvorom od jedne do osam godina.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Ako ukupan iznos na koji glase falsifikovane hartije od vrijednosti iz stava 1 ovog člana prelaza trideset hiljada eura, učinilac će se kazniti zatvorom od dvije do deset godina.
              </div>
              <div class="paragraph">
                <strong>(4)</strong> Ko lažne hartije od vrijednosti koje je primio kao prave, pa saznavši da su lažne, stavi u promet, kazniće se novčanom kaznom ili zatvorom do jedne godine.
              </div>
              <div class="paragraph">
                <strong>(5)</strong> Lažne hartije od vrijednosti oduzeće se.
              </div>
            </div>
          </div>

          <!-- Član 260 - Falsifikovanje i zloupotreba kreditnih kartica i kartica za bezgotovinsko plaćanje -->
          <div class="article" id="260">
            <div class="article-number">Član 260 - Falsifikovanje i zloupotreba kreditnih kartica i kartica za bezgotovinsko plaćanje</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko napravi lažnu platnu karticu ili ko preinači pravu platnu karticu u namjeri da je upotrijebi kao pravu, ili ko takvu lažnu platnu karticu ili tuđu pravu platnu karticu koja je neovlašćeno pribavljena nabavi, drži ili prenese radi upotrebe ili takvu karticu upotrijebi, kazniće se zatvorom do tri godine.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Ako je učinilac djela iz stava 1 ovog člana upotrebom kartice pribavio protivpravnu imovinsku korist, kazniće se zatvorom od šest mjeseci do pet godina.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Ako je učinilac djela iz stava 1 ovog člana pribavio protivpravnu imovinsku korist u iznosu koji prelaza tri hiljade eura, kazniće se zatvorom od jedne do osam godina.
              </div>
              <div class="paragraph">
                <strong>(4)</strong> Ako je učinilac djela iz stava 1 ovog člana pribavio protivpravnu imovinsku korist u iznosu koji prelaza trideset hiljada eura, kazniće se zatvorom od dvije do deset godina.
              </div>
              <div class="paragraph">
                <strong>(5)</strong> (brisano)
              </div>
            </div>
          </div>

          <!-- Član 261 - Falsifikovanje znakova za vrijednost -->
          <div class="article" id="261">
            <div class="article-number">Član 261 - Falsifikovanje znakova za vrijednost</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko napravi lažne ili preinači prave znakove za vrijednost u namjeri da ih upotrijebi kao prave ili da ih drugom da na upotrebu ili ko takve lažne znakove upotrijebi kao prave ili ih u toj namjeri pribavi, kazniće se zatvorom do tri godine.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Ako ukupna vrijednost znakova iz stava 1 ovog člana prelaza iznos od tri hiljade eura, učinilac će se kazniti zatvorom od šest mjeseci do pet godina.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Ako ukupna vrijednost znakova iz stava 1 ovog člana prelaza iznos od trideset hiljada eura, učinilac će se kazniti zatvorom od jedne do osam godina.
              </div>
              <div class="paragraph">
                <strong>(4)</strong> Ko odstranjivanjem žiga kojim se znaci za vrijednost poništavaju ili kojim drugim načinom ide za tim da radi ponovne upotrebe ovim znacima da izgled kao da nijesu upotrijebljeni ili ko upotrijebljene znakove ponovo upotrijebi ili proda kao da važe, kazniće se novčanom kaznom ili zatvorom do jedne godine.
              </div>
              <div class="paragraph">
                <strong>(5)</strong> Lažni znakovi za vrijednost oduzeće se.
              </div>
            </div>
          </div>

          <!-- Član 262 - Pravljenje, nabavljanje i davanje drugom sredstava i materijala za falsifikovanje -->
          <div class="article" id="262">
            <div class="article-number">Član 262 - Pravljenje, nabavljanje i davanje drugom sredstava i materijala za falsifikovanje</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko pravi, nabavlja, prodaje, drži radi upotrebe ili daje drugom na upotrebu sredstva i materijal za pravljenje lažnog novca, platnih kartica ili lažnih hartija od vrijednosti, kazniće se zatvorom od šest mjeseci do pet godina.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Kaznom iz stava 1 ovog člana kazniće se i ko, radi pravljenja lažnog novca, pravi, nabavlja, prodaje, drži radi upotrebe, drži ili daje drugom holograme ili druge sastavne dijelove novca koji služe za zaštitu od falsifikovanja.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Ko pravi, nabavlja, prodaje, drži radi upotrebe ili daje drugom na upotrebu sredstva za pravljenje lažnih znakova za vrijednost, kazniće se novčanom kaznom ili zatvorom do dvije godine.
              </div>
              <div class="paragraph">
                <strong>(4)</strong> Sredstva iz st. 1 do 3 ovog člana oduzeće se.
              </div>
            </div>
          </div>

          <!-- Član 263 - Izdavanje čeka i sredstava bezgotovinskog plaćanja bez pokrića -->
          <div class="article" id="263">
            <div class="article-number">Član 263 - Izdavanje čeka i sredstava bezgotovinskog plaćanja bez pokrića</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko koristi kreditnu karticu za koju zna da neće obezbijediti pokriće u ugovorenom roku, pa time sebi ili drugome pribavi protivpravnu imovinsku korist koja prelaza pet stotina eura, kazniće se novčanom kaznom ili kaznom zatvora do tri godine.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Kaznom iz stava 1 ovog člana kazniće se i ko izda ili stavi u promet ček, mjenicu, kakvu garanciju ili kakvo drugo sredstvo plaćanja ili obezbjeđenja plaćanja, iako zna da za to nema pokrića i time sebi ili drugom pribavi protivpravnu imovinsku korist u iznosu koji prelaza pet stotina eura.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Ako je djelom iz st. 1 i 2 ovog člana pribavljena imovinska korist u iznosu koji prelaza tri hiljade eura, učinilac će se kazniti zatvorom od jedne do osam godina.
              </div>
              <div class="paragraph">
                <strong>(4)</strong> Ako je djelom iz st. 1 i 2 ovog člana pribavljena imovinska korist u iznosu koji prelaza trideset hiljada eura, učinilac će se kazniti zatvorom od dvije do deset godina.
              </div>
            </div>
          </div>

          <!-- Član 264 - Utaja poreza i doprinosa -->
          <div class="article" id="264">
            <div class="article-number">Član 264 - Utaja poreza i doprinosa</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko, u namjeri da on ili neko drugo fizičko ili pravno lice potpuno ili djelimično izbjegne plaćanje poreza, doprinosa ili drugih propisanih dažbina, daje lažne podatke o zakonito stečenim prihodima, o predmetima ili drugim činjenicama koje su od uticaja na utvrđivanje ovakvih obaveza ili ko u istoj namjeri, u slučaju obavezne prijave, ne prijavi zakonito stečeni prihod, odnosno predmete ili druge činjenice koje su od uticaja na utvrđivanje ovakvih obaveza ili ko u istoj namjeri na drugi način prikriva podatke koji se odnose na utvrđivanje navedenih obaveza, a iznos obaveze čije se plaćanje izbjegava prelaza hiljadu eura, kazniće se zatvorom do tri godine i novčanom kaznom.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Ako je djelo iz stava 1 ovog člana učinjeno na štetu finansijskih interesa Evropske Unije, učinilac će se kazniti kaznom propisanom za to djelo.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Ako iznos obaveze iz st. 1 i 2 ovog člana čije se plaćanje izbjegava prelaza deset hiljada eura, učinilac će se kazniti zatvorom od jedne do šest godina i novčanom kaznom.
              </div>
              <div class="paragraph">
                <strong>(4)</strong> Ako iznos obaveze iz st. 1 i 2 ovog člana čije se plaćanje izbjegava prelaza sto hiljada eura, učinilac će se kazniti zatvorom od jedne do osam godina i novčanom kaznom.
              </div>
            </div>
          </div>

          <!-- Član 265 - Krijumčarenje -->
          <div class="article" id="265">
            <div class="article-number">Član 265 - Krijumčarenje</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko se bavi prenošenjem robe preko carinske linije izbjegavajući mjere carinskog nadzora ili ko izbjegavajući mjere carinskog nadzora prenese robu preko carinske linije naoružan, u grupi ili uz upotrebu sile ili prijetnje, kazniće se zatvorom od šest mjeseci do pet godina i novčanom kaznom.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Ko prenese preko carinske linije, izbjegavajući mjere carinskog nadzora, veću količinu oružja ili municije ili oružje čije držanje je građanima zabranjeno ili drugu robu čija je proizvodnja ili promet ograničen ili zabranjen, kazniće se zatvorom od jedne do osam godina i novčanom kaznom.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Ko se bavi prodajom, rasturanjem ili prikrivanjem neocarinjene robe ili organizuje mrežu preprodavaca ili posrednika za rasturanje takve robe, kazniće se zatvorom od jedne do osam godina i novčanom kaznom.
              </div>
              <div class="paragraph">
                <strong>(4)</strong> Roba koja je predmet djela iz st. 1, 2 i 3 ovog člana oduzeće se.
              </div>
              <div class="paragraph">
                <strong>(5)</strong> Prevozno sredstvo čija su tajna ili skrovita mjesta iskorišćena za prenos robe koja je predmet djela iz stava 1 ovog člana ili koje je namijenjeno za izvršenje tih krivičnih djela može se oduzeti ako je vlasnik ili korisnik vozila to znao ili je mogao i bio dužan da zna i ako vrijednost robe koja je predmet krivičnog djela prelaza jednu trećinu vrijednosti prevoznog sredstva u vrijeme izvršenja krivičnog djela.
              </div>
            </div>
          </div>

          <!-- Član 266 - Nedozvoljeno bavljenje privrednom, bankarskom, berzanskom i djelatnošću osiguranja -->
          <div class="article" id="266">
            <div class="article-number">Član 266 - Nedozvoljeno bavljenje privrednom, bankarskom, berzanskom i djelatnošću osiguranja</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko se bez registracije ili odobrenja ili protivno uslovima pod kojima je ono dato bavi privrednom ili drugom djelatnošću ili ko registruje privredno društvo ili se registruje za obavljanje privredne djelatnosti kao preduzetnik protivno zabrani za registrovanje privrednog društva ili preduzetnika, kazniće se kaznom zatvora od tri mjeseca do pet godina i novčanom kaznom.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Ko se bez odobrenja ili protivno uslovima pod kojima je ono dato bavi bankarskom, berzanskom ili djelatnošću osiguranja, kazniće se zatvorom od tri mjeseca do pet godina.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Za djelo iz stava 2 ovog člana kazniće se propisanom kaznom i odgovorno lice u pravnom licu, ako se pravno lice nedozvoljeno bavi nekom od navedenih djelatnosti, ukoliko je odgovorno lice za to znalo ili je to moglo i bilo dužno da zna.
              </div>
            </div>
          </div>

          <!-- Član 267 - Izdavanje hartija od vrijednosti bez pokrića -->
          <div class="article" id="267">
            <div class="article-number">Član 267 - Izdavanje hartija od vrijednosti bez pokrića</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Odgovorno lice u banci, privrednom društvu ili drugom subjektu privrednog poslovanja koji izdaje hartije od vrijednosti, koje dozvoli izdavanje hartija od vrijednosti, iako je znalo ili je moglo i bilo dužno da zna za nemogućnost izvršenja obaveza izdavaoca koje proizlaze iz emisije, pod uslovima, u roku i na način utvrđen zakonom ili odlukom o emisiji, kazniće se novčanom kaznom ili zatvorom do jedne godine.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Službeno lice koje odobri izdavanje hartija od vrijednosti iako je znalo ili je moglo i bilo dužno da zna za nemogućnost izvršenja obaveza koje proizlaze iz emisije pod uslovima, u roku i na način utvrđen zakonom ili odlukom o emisiji, kazniće se zatvorom do jedne godine.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Odgovorno lice u banci koje odobri garanciju po određenoj emisiji hartija od vrijednosti iako je znalo ili je moglo i bilo dužno da zna za nemogućnost izvršenja garancijom preuzete obaveze banke, pod uslovima, u roku i na način predviđen zakonom ili garancijom, kazniće se novčanom kaznom ili zatvorom do šest mjeseci.
              </div>
            </div>
          </div>

          <!-- Član 268 - Pranje novca -->
          <div class="article" id="268">
            <div class="article-number">Član 268 - Pranje novca</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko izvrši konverziju ili prenos novca ili druge imovine sa znanjem da su pribavljeni kriminalnom djelatnošću, u namjeri da se prikrije ili lažno prikaže porijeklo novca ili druge imovine, ili ko stekne, drži ili koristi novac ili drugu imovinu sa znanjem u trenutku prijema da potiču od vršenja kriminalne djelatnosti, ili ko prikrije ili lažno prikaže činjenice o prirodi, porijeklu, mjestu deponovanja, kretanja, raspolaganja ili vlasništva novca ili druge imovine za koje zna da su pribavljeni kriminalnom djelatnošću, kazniće se zatvorom od šest mjeseci do pet godina.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Kaznom iz stava 1 ovog člana kazniće se izvršilac djela iz stava 1 ovog člana koji je i izvršilac ili saučesnik u krivičnom djelu kojim je pribavljen novac ili imovina iz stava 1 ovog člana ili ko pomogne izvršiocu radi izbjegavanja njegove odgovornosti za učinjeno djelo, ili u istom cilju preduzme radnje radi prikrivanja porijekla novca ili imovine iz stava 1 ovog člana.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Ako iznos novca ili vrijednost imovine iz st. 1 i 2 ovog člana prelaza četrdeset hiljada eura, učinilac će se kazniti zatvorom od jedne do deset godina.
              </div>
              <div class="paragraph">
                <strong>(4)</strong> Ako djelo iz st. 1 i 2 ovog člana izvrši više lica koja su se udružila za vršenje takvih djela, kazniće se zatvorom od tri do dvanaest godina.
              </div>
              <div class="paragraph">
                <strong>(5)</strong> Ko učini djelo iz st. 1 i 2 ovog člana, a mogao je i bio dužan da zna da novac ili imovina predstavljaju prihod pribavljen kriminalnom djelatnošću, kazniće se zatvorom do tri godine.
              </div>
              <div class="paragraph">
                <strong>(6)</strong> Novac i imovina iz st. 1, 2 i 3 ovog člana oduzeće se.
              </div>
              <div class="paragraph">
                <strong>(7)</strong> Imovina, u smislu ovog člana, podrazumijeva imovinska prava bilo koje vrste, nezavisno od toga da li se odnose na dobra materijalne ili nematerijalne prirode, pokretne ili nepokretne stvari, hartije od vrijednosti i druge isprave kojima se dokazuju imovinska prava.
              </div>
            </div>
          </div>

          <!-- Član 269 - Povreda ravnopravnosti u vršenju privredne djelatnosti -->
          <div class="article" id="269">
            <div class="article-number">Član 269 - Povreda ravnopravnosti u vršenju privredne djelatnosti</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko zloupotrebom svog službenog položaja ili ovlašćenja ograniči slobodno ili samostalno povezivanje privrednog društva ili drugog subjekta privrednog poslovanja u obavljanju privredne djelatnosti, uskrati mu ili organiči pravo da na određenom području obavlja privrednu djelatnost, stavi ga u neravnopravan položaj prema drugim subjektima privrednog poslovanja u pogledu uslova privređivanja ili ograniči slobodno obavljanje privredne djelatnosti, kazniće se zatvorom od tri mjeseca do pet godina.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Kaznom iz stava 1 ovog člana kazniće se ko zloupotrijebi svoj društveni položaj ili uticaj radi izvršenja krivičnog djela iz stava 1 ovog člana.
              </div>
            </div>
          </div>

          <!-- Član 270 - Zloupotreba monopolističkog položaja -->
          <div class="article" id="270">
            <div class="article-number">Član 270 - Zloupotreba monopolističkog položaja</div>
            <div class="article-content">
              <div class="paragraph">
                Odgovorno lice u privrednom društvu ili u drugom subjektu privrednog poslovanja, koji zloupotrebom monopolističkog ili dominantnog položaja na tržištu ili zaključivanjem monopolističkog sporazuma izazove poremećaj na tržištu ili taj subjekat dovede u povlašćen položaj u odnosu na druge, tako da ostvari imovinsku korist za taj subjekat ili za drugi subjekat ili nanese štetu drugim subjektima privrednog poslovanja, potrošačima ili korisnicima usluga, kazniće se zatvorom od tri mjeseca do pet godina.
              </div>
            </div>
          </div>

          <!-- Član 271 - Neovlašćena upotreba tuđe firme -->
          <div class="article" id="271">
            <div class="article-number">Član 271 - Neovlašćena upotreba tuđe firme</div>
            <div class="article-content">
              <div class="paragraph">
                Ko se u namjeri da obmane kupce ili korisnike usluga posluži tuđom firmom, tuđom geografskom oznakom porijekla, tuđim žigom ili zaštitnim znakom ili tuđom posebnom oznakom robe ili unese pojedina obilježja ovih oznaka u svoju firmu, svoj žig ili zaštitni znak ili u svoju posebnu oznaku robe, kazniće se novčanom kaznom ili zatvorom do tri godine.
              </div>
            </div>
          </div>

          <!-- Član 272 - Zloupotreba položaja u privrednom poslovanju -->
          <div class="article" id="272">
            <div class="article-number">Član 272 - Zloupotreba položaja u privrednom poslovanju</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Odgovorno lice u privrednom društvu, drugom subjektu privrednog poslovanja ili drugom pravnom licu koje zloupotrebom svog položaja ili povjerenja u pogledu raspolaganja tuđom imovinom, prekoračenjem granica svog ovlašćenja ili nevršenja svoje dužnosti pribavi sebi ili drugom protivpravnu imovinsku korist ili drugom nanese imovinsku štetu, kazniće se zatvorom od tri mjeseca do pet godina.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Kaznom iz stava 1 ovog člana kazniće se i ko, u namjeri da sebi ili drugom pribavi protivpravnu imovinsku korist, prisvoji novac, hartije od vrijednosti ili druge pokretne stvari koje su mu povjerene na radu u privrednom društvu, drugom subjektu privrednog poslovanja ili drugom pravnom licu.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Ako je usljed djela iz st. 1 i 2 ovog člana pribavljena imovinska korist koja prelaza iznos od četrdeset hiljada eura, učinilac će se kazniti zatvorom od dvije do deset godina.
              </div>
            </div>
          </div>

          <!-- Član 273 -->
          <div class="article" id="273">
            <div class="article-number">Član 273</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Odgovorno lice u privrednom društvu ili u drugom subjektu privrednog poslovanja, koje neracionalnim trošenjem sredstava ili njihovim otuđenjem u bescijenje, prekomjernim zaduživanjem, preuzimanjem nesrazmjernih obaveza, lakomislenim zaključivanjem ugovora sa licima nesposobnim za plaćanje, propuštanjem blagovremenog ostvarivanja potraživanja, uništenjem ili prikrivanjem imovine ili drugim radnjama koje nijesu u skladu sa savjesnim poslovanjem prouzrokuje stečaj i time drugog ošteti, kazniće se zatvorom od šest mjeseci do pet godina.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> (brisano)
              </div>
            </div>
          </div>

          <!-- Član 274 - Prouzrokovanje lažnog stečaja -->
          <div class="article" id="274">
            <div class="article-number">Član 274 - Prouzrokovanje lažnog stečaja</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Odgovorno lice u privrednom društvu ili u drugom subjektu privrednog poslovanja, koji u namjeri da taj subjekt izbjegne plaćanje obaveza prouzrokuje stečaj tog subjekta prividnim ili stvarnim umanjenjem njegove imovine, na način što:
              </div>
              <div class="paragraph">
                1) cijelu ili dio imovine subjekta privrednog poslovanja prikrije, prividno proda, proda ispod tržišne vrijednosti ili basplatno ustupi;
              </div>
              <div class="paragraph">
                2) zaključi fiktivne ugovore o dugu ili prizna nepostojeća potraživanja;
              </div>
              <div class="paragraph">
                3) poslovne knjige koje je subjekt privrednog poslovanja obavezan da vodi po zakonu prikrije, uništi ili tako preinači da se iz njih ne mogu sagledati poslovni rezultati ili stanje sredstava ili obaveza ili ovo stanje sačinjavanjem lažnih isprava ili na drugi način prikaže takvim da se na osnovu njega može otvoriti stečaj, kazniće se zatvorom od šest mjeseci do pet godina.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Ako su usljed djela iz stava 1 ovog člana nastupile teške posljedice za povjerioca, učinilac će se kazniti zatvorom od dvije do deset godina.
              </div>
            </div>
          </div>

          <!-- Član 275 - Oštećenje povjerioca -->
          <div class="article" id="275">
            <div class="article-number">Član 275 - Oštećenje povjerioca</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Odgovorno lice u privrednom društvu ili drugom subjektu privrednog poslovanja, koje znajući da je taj subjekt postao nesposoban za plaćanje, isplatom duga ili na drugi način namjerno stavi povjerioca u povoljniji položaj i time znatno ošteti drugog povjerioca, kazniće se zatvorom od tri mjeseca do tri godine.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Odgovorno lice iz stava 1 ovog člana ili preduzetnik, koji znajući da je taj subjekt postao nesposoban za plaćanje, a u namjeri da izigra ili ošteti povjerioca prizna neistinito potraživanje, sastavi lažni ugovor ili nekom drugom prevarnom radnjom ošteti povjerioca, kazniće se zatvorom od tri mjeseca do pet godina.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Ako je djelom iz st. 1 i 2 ovog člana povjeriocu prouzrokovana šteta koja prelaza iznos od četrdeset hiljada eura ili ako je prema oštećenom zbog toga došlo do pokretanja postupka prinudnog poravnjanja ili stečaja, učinilac će se kazniti zatvorom od jedne do osam godina.
              </div>
            </div>
          </div>

          <!-- Član 276 - Zloupotreba ovlašćenja u privredi -->
          <div class="article" id="276">
            <div class="article-number">Član 276 - Zloupotreba ovlašćenja u privredi</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Odgovorno lice u privrednom društvu ili drugom subjektu privrednog poslovanja koje u namjeri pribavljanja protivpravne imovinske koriti za pravno lice u kojem je zaposleno, za drugo pravno lice ili drugi subjekt privrednog poslovanja:
              </div>
              <div class="paragraph">
                1) stvara ili drži nedozvoljene novčane, robne ili druge vrijednosni fondove u zemlji ili inostranstvu;
              </div>
              <div class="paragraph">
                2) sastavljanjem isprave neistinite sadžine, procjenama ili inventarisanjem odnosno lažnim prikazivanjem ili prikrivanjem činjenica, neistinito prikazuje stanje ili kretanje sredstava ili rezultate poslovanja, pa na taj način dovede u zabludu organe upravljanja u privrednom društvu ili drugom pravnom licu prilikom donošenja odluka o poslovima upravljanja ili privredno društo ili drugo pravno lice stavi u povoljniji položaj prilikom dobijanja sredstava ili drugih pogodnosti koje im se ne bi priznale prema postojećim propisima;
              </div>
              <div class="paragraph">
                3) sredstva kojima raspolaže koristi protivno njihovoj namjeni;
              </div>
              <div class="paragraph">
                4) na drugi način grubo povrijedi ovlašćenja u pogledu upravljanja, raspolaganja i korišćenja imovinom, kazniće se zatvorom od tri mjeseca do pet godina.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Ako je usljed djela iz stava 1 ovog člana pribavljena imovinska korist koja prelaza iznos od četrdeset hiljada eura, učinilac će se kazniti zatvorom od dvije do dvanaest godina.
              </div>
            </div>
          </div>

          <!-- Član 276a - Primanje mita u privrednom poslovanju -->
          <div class="article" id="276a">
            <div class="article-number">Član 276a - Primanje mita u privrednom poslovanju</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Odgovorno ili drugo lice koje radi za ili u privrednom društvu ili drugom subjektu privrednog poslovanja koje za sebe ili drugog, neposredno ili posredno, zahtijeva ili primi mito ili prihvati obećanje mita da zaključi ugovor ili postigne poslovni dogovor ili pruži uslugu ili da se uzdrži od takvog djelovanja na štetu ili u korist privrednog društva za koje ili u kojem radi ili drugog lica, kazniće se zatvorom od jedne do osam godina.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Učinilac djela iz stava 1 ovog člana koji, poslije zaključenja ugovora ili postizanja poslovnog dogovora ili poslije pružene usluge ili uzdržavanja od takvog djelovanja, za sebe ili drugog zahtijeva ili primi mito ili prihvati obećanje mita, kazniće se zatvorom do tri godine.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Primljeno mito oduzeće se.
              </div>
            </div>
          </div>

          <!-- Član 276b - Davanje mita u privrednom poslovanju -->
          <div class="article" id="276b">
            <div class="article-number">Član 276b - Davanje mita u privrednom poslovanju</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko da, ponudi ili obeća mito odgovornom ili drugom licu koje radi za ili u privrednom društvu ili drugom subjektu privrednog poslovanja da, za sebe ili drugog, zaključi ugovor ili postigne poslovni dogovor ili pruži uslugu na štetu ili u korist privrednog društva za koje ili u kojem radi ili drugog lica ili ko posreduje pri ovakvom davanju mita, kazniće se zatvorom od šest mjeseci do pet godina.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Učinilac djela iz stava 1 ovog člana koji je dao mito na zahtjev odgovornog ili drugog lica koje radi za ili u privrednom društvu ili drugom subjektu privrednog poslovanja, a djelo je prijavio prije nego što je saznao da je ono otkriveno, može se osloboditi od kazne.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Dato mito oduzeće se.
              </div>
            </div>
          </div>

          <!-- Član 277 - Narušavanje poslovnog ugleda i kreditne sposobnosti -->
          <div class="article" id="277">
            <div class="article-number">Član 277 - Narušavanje poslovnog ugleda i kreditne sposobnosti</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko u namjeri narušavanja poslovnog ugleda ili kreditne sposobnosti drugog, iznosi o njemu neistinite podatke ili neistinito prikazuje njegovo poslovanje, kazniće se novčanom kaznom ili zatvorom do jedne godine.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Ako su usljed djela iz stava 1 ovog člana nastupile teške posljedice, učinilac će se kazniti zatvorom od tri mjeseca do tri godine.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Gonjenje za djela iz st. 1 i 2 ovog člana preduzima se po privatnoj tužbi.
              </div>
            </div>
          </div>

          <!-- Član 278 - Lažan bilans -->
          <div class="article" id="278">
            <div class="article-number">Član 278 - Lažan bilans</div>
            <div class="article-content">
              <div class="paragraph">
                Ko u namjeri da sebi ili drugom pribavi kakvu korist ili drugom nanese kakvu štetu, sačini u privrednom društvu ili drugom subjektu privrednog poslovanja lažan bilans kojim se utvrđuje dobit ili gubitak tog subjekta ili kojim se utvrđuje udio svakog člana društva u dobiti ili gubitku, kazniće se zatvorom od tri mjeseca do pet godina.
              </div>
            </div>
          </div>

          <!-- Član 279 - Zloupotreba procjene -->
          <div class="article" id="279">
            <div class="article-number">Član 279 - Zloupotreba procjene</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ovlašćeni procjenjivač koji prilikom procjene imovine privrednog društva ili drugog subjekta privrednog poslovanja zloupotrijebi svoje ovlašćenje i time sebi ili drugom pribavi kakvu korist ili drugom nanese kakvu štetu, kazniće se zatvorom od tri mjeseca do pet godina.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Ako je djelom iz stava 1 ovog člana pribavljena imovinska korist ili prouzrokovana šteta koja prelaza iznos od tri hiljade eura, učinilac će se kazniti zatvorom od jedne do osam godina.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Ako je djelom iz stava 1 ovog člana pribavljena imovinska korist ili prouzrokovana šteta koja prelaza iznos od trideset hiljada eura, učinilac će se kazniti zatvorom od dvije do deset godina.
              </div>
            </div>
          </div>

          <!-- Član 280 - Odavanje poslovne tajne -->
          <div class="article" id="280">
            <div class="article-number">Član 280 - Odavanje poslovne tajne</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko neovlašćeno drugom saopšti, preda ili na drugi način učini dostupnim podatke koji predstavljaju poslovnu tajnu ili ko pribavlja takve podatke u namjeri da ih preda nepozvanom licu, kazniće se zatvorom od tri mjeseca do pet godina.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Kaznom iz stava 1 ovog člana kazniće se i nepozvano lice koje koristi podatke koji predstavljaju poslovnu tajnu pribavljene na način iz stava 1 ovog člana.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Ako je djelo iz st. 1 i 2 ovog člana učinjeno iz koristoljublja ili u pogledu naročito povjerljivih podataka ili radi objavljivanja ili korišćenja podataka u inostranstvu, učinilac će se kazniti zatvorom od dvije do deset godina.
              </div>
              <div class="paragraph">
                <strong>(4)</strong> Ko djelo iz st. 1 i 2 ovog člana učini iz nehata, kazniće se zatvorom do tri godine.
              </div>
              <div class="paragraph">
                <strong>(5)</strong> Poslovnom tajnom smatraju se podaci i dokumenti koji su zakonom, drugim propisom ili odlukom nadležnog organa donesenom na osnovu zakona proglašeni poslovnom tajnom čije bi odavanje prouzrokovalo ili bi moglo da prouzrokuje štetne posljedice za privredno društvo ili drugi subjekt privrednog poslovanja.
              </div>
            </div>
          </div>

          <!-- Član 281 - Zloupotreba povlašćenih informacija -->
          <div class="article" id="281">
            <div class="article-number">Član 281 - Zloupotreba povlašćenih informacija</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko u namjeri da sebi ili drugom pribavi imovinsku korist ili nanese štetu drugom saopšti ili na drugi način učini dostupnim povlašćenu informaciju nepozvanom licu ili koristeći povlašćenu informaciju, za sebe ili drugog, neposredno ili posredno, pribavi ili otuđi hartiju od vrijednosti ili drugi finansijski instrument na koji se ta informacija odnosi ili ko preporuči drugom ili ga navede da pribavi ili otuđi hartiju od vrijednosti ili drugi finansijski instrument na koji se ta informacija odnosi, kazniće se novčanom kaznom ili zatvorom do tri godine.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Kaznom iz stava 1 ovog člana kazniće se i nepozvano lice koje koristi povlašćene informacije koje su pribavljene na način iz stava 1 ovog člana.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Ako djelo iz stava 1 ovog člana učini lice koje je član odbora direktora ili nadzornog organa emitenta ili ima udio u kapitalu emitenta, kazniće se zatvorom od šest mjeseci do pet godina.
              </div>
              <div class="paragraph">
                <strong>(4)</strong> Ako je djelom iz st. 1, 2 i 3 ovog člana pribavljena imovinska korist koja prelaza iznos od tri hiljade eura, učinilac će se kazniti zatvorom od jedne do osam godina.
              </div>
              <div class="paragraph">
                <strong>(5)</strong> Ako je djelom iz st. 1, 2 i 3 ovog člana pribavljena imovinska korist koja prelaza iznos od trideset hiljada eura, učinilac će se kazniti zatvorom od dvije do deset godina.
              </div>
              <div class="paragraph">
                <strong>(6)</strong> Za pokušaj djela iz stava 1 ovog člana kazniće se.
              </div>
            </div>
          </div>

          <!-- Član 281a - Manipulacija na tržištu hartija od vrijednosti ili drugih finansijskih instrumenata -->
          <div class="article" id="281a">
            <div class="article-number">Član 281a - Manipulacija na tržištu hartija od vrijednosti ili drugih finansijskih instrumenata</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko u namjeri da sebi ili drugom pribavi imovinsku korist ili nanese štetu drugom postupa suprotno propisima o tržištu hartija od vrijednosti, na način što:
              </div>
              <div class="paragraph">
                1) zaključi transakciju ili da nalog za trgovanje kojim se daju ili mogu dati netačne ili obmanjujuće informacije o ponudi, tražnji ili cijeni hartija od vrijednosti ili drugih finansijskih instrumenata ili kojima lice ili lica koja djeluju zajednički održavaju cijenu jedne ili više hartija od vrijednosti ili drugih finansijskih instrumenata na nerealnom nivou;
              </div>
              <div class="paragraph">
                2) prilikom zaključivanja transakcije ili davanja naloga za trgovanje zadrži, poveća, smanji ili izazove promjene u tržišnoj cijeni hartija od vrijednosti ili drugih finansijskih instrumenata putem kupovine ili prodaje ili fiktivnom transakcijom kojom se ne izvrši promjena vlasništva nad tom hartijom od vrijednosti ili drugim finansijskim instrumentom;
              </div>
              <div class="paragraph">
                3) putem medija, interneta ili na drugi način širi ili prenosi netačne ili obmanjujuće informacije koje mogu izazvati zabludu o hartijama od vrijednosti ili drugim finansijskim instrumentima, a znao je da su te informacije netačne ili obmanjujuće i da mogu dovesti u zabludu korisnika informacije, kazniće se zatvorom od šest mjeseci do pet godina i novčanom kaznom.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Ako je djelom iz stava 1 ovog člana pribavljena imovinska korist koja prelaza iznos od trideset hiljada eura, učinilac će se kazniti zatvorom od dvije do deset godina i novčanom kaznom.
              </div>
            </div>
          </div>

          <!-- Član 282 - Onemogućavanje vršenja kontrole -->
          <div class="article" id="282">
            <div class="article-number">Član 282 - Onemogućavanje vršenja kontrole</div>
            <div class="article-content">
              <div class="paragraph">
                Ko onemogući inspekcijskom ili drugom organu vršenja kontrole da izvrši uvid u poslovne knjige ili drugu dokumentaciju ili onemogući pregled predmeta, prostorija ili drugih objekata, kazniće se novčanom kaznom ili zatvorom do jedne godine.
              </div>
            </div>
          </div>

          <!-- Član 283 - Nedozvoljena proizvodnja -->
          <div class="article" id="283">
            <div class="article-number">Član 283 - Nedozvoljena proizvodnja</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko neovlašćeno proizvodi ili prerađuje robu za čiju je proizvodnju ili prerađivanje potrebno odobrenje nadležnog organa, kazniće se novčanom kaznom ili zatvorom do dvije godine.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Ko proizvodi ili prerađuje robu čija je proizvodnja ili prerađivanje zabranjeno, kazniće se zatvorom do tri godine.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Roba i sredstva za proizvodnju ili prerađivanje oduzeće se.
              </div>
            </div>
          </div>

          <!-- Član 284 - Nedozvoljena trgovina -->
          <div class="article" id="284">
            <div class="article-number">Član 284 - Nedozvoljena trgovina</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko nemajući ovlašćenje za trgovinu, u svrhu prodaje nabavi robu ili druge predmete opšte upotrebe u vrijednosti koja prelaza iznos od tri hiljade eura ili ko se neovlašćeno i u većem obimu bavi trgovinom ili posredovanjem u trgovini ili zastupanjem organizacija u unutrašnjem ili spoljnotrgovinskom prometu roba i usluga, kazniće se novčanom kaznom ili zatvorom do dvije godine.
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Ko se bavi prodajom robe čiju je proizvodnju neovlašćeno organizovao, kazniće se zatvorom od tri mjeseca do tri godine.
              </div>
              <div class="paragraph">
                <strong>(3)</strong> Kaznom iz stava 2 ovog člana kazniće se i ko neovlašćeno prodaje, kupuje ili vrši razmjenu robe ili predmeta čiji je promet zabranjem ili ograničen.
              </div>
              <div class="paragraph">
                <strong>(4)</strong> Ako je učinilac djela iz st. 1 do 3 ovog člana organizovao mrežu preprodavaca ili posrednika ili je postigao imovinsku korist koja prelaza iznos od tri hiljade eura, kazniće se zatvorom od šest mjeseci do pet godina.
              </div>
              <div class="paragraph">
                <strong>(5)</strong> Ako je učinilac djela iz st. 1 i 3 ovog člana postigao imovinsku korist koja prelaza iznos od trideset hiljada eura, kazniće se zatvorom od jedne do šest godina.
              </div>
              <div class="paragraph">
                <strong>(6)</strong> Roba i predmeti nedozvljene trgovine oduzeće se.
              </div>
            </div>
          </div>

          <!-- Član 285 - Obmanjivanje kupaca -->
          <div class="article" id="285">
            <div class="article-number">Član 285 - Obmanjivanje kupaca</div>
            <div class="article-content">
              <div class="paragraph">
                Ko u namjeri obmanjivanja kupaca stavlja u promet proizvode sa oznakom u koju su unijeti podaci koji ne odgovaraju sadržini, vrsti, porijeklu ili kvalitetu proizvoda ili stavlja u promet proizvode koji po svojoj količini ili kvalitetu ne odgovaraju onome što se redovno pretpostavlja kod takvih proizvoda ili stavlja u promet proizvode bez oznake o sadržini, vrsti porijeklu ili kvalitetu proizvoda kad je ovakva oznaka propisana ili se pri stavljanju u promet proizvoda služi očigledno lažnom reklamom, kazniće se zatvorom do tri godine i novčanom kaznom.
              </div>
            </div>
          </div>

          <!-- Član 286 - Falsifikovanje znakova za obilježavanje robe -->
          <div class="article" id="286">
            <div class="article-number">Član 286 - Falsifikovanje znakova za obilježavanje robe</div>
            <div class="article-content">
              <div class="paragraph">
                <strong>(1)</strong> Ko u namjeri da ih upotrijebi kao prave napravi lažne pečate, žigove, marke ili druge znakove za obilježavanje domaće ili strane robe kojima se žigošu zlato ili drugi plemeniti metal, drvo, stoka ili kakva druga roba ili ko u istoj namjeri takve prave znakove preinači ili ko takve lažne ili preinačene znakove upotrijebi kao prave, kazniće se novčanom kaznom ili zatvorom do dvije godine
              </div>
              <div class="paragraph">
                <strong>(2)</strong> Lažni znakovi oduzeće se i uništiti.
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>'''

# Find and replace the old articles section
# Look for the start of the articles (after the glava-subtitle)
import re

# Pattern to find the articles section - from first <!-- Član 258 --> to the closing </div></div></div>
pattern = r'(<!-- Član 258 -->.*?</div>\n      </div>\n    </div>)'

if re.search(pattern, content, re.DOTALL):
    new_content = re.sub(pattern, new_articles + '\n      </div>\n    </div>', content, flags=re.DOTALL)
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Successfully replaced all articles with Latinica version")
    print("✅ All articles 258-286 now in pure Serbian Latinica")
else:
    print("❌ Could not find articles section to replace")
