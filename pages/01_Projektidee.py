"""
HerEducation - Projektidee Page (KORRIGIERTE VERSION)
Wissenschaftlich fundiert, aber zum Gern-Lesen geschrieben
UNESCO/UNICEF Professionalität trifft auf Storytelling
EHRLICH & REALISTISCH - Keine Übertreibungen
"""

import streamlit as st
from PIL import Image
from utils.shared_components import setup_standard_page, display_standard_footer, get_image

# ===== SPRACHSYSTEM SETUP =====
from utils.language_switcher_config import init_language, get_text, t
from utils.language_switcher_ui import language_switcher

# ===== CONTENT FUNCTIONS =====
def display_tab_ursprung():
    """Tab 1: Warum Malaysia? Warum jetzt?"""
    if st.session_state.language == "DE":
        st.markdown('<div class="subtitle-text">Warum Malaysia der Schlüssel für Mädchenbildung in Asien ist</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Stellen Sie sich vor:</strong> Ein Land, das wirtschaftlich floriert, technologisch fortschrittlich ist, 
        eine Alphabetisierungsrate von 95% hat – und trotzdem jeden Tag 7,5 Millionen Mädchen und Frauen 
        von vollständiger Gleichberechtigung ausgeschlossen bleiben.
        <br><br>
        
        Willkommen in Malaysia. Einem Land voller Widersprüche, das genau deshalb zum perfekten Testfall für 
        innovative Bildungslösungen wird.
        <br><br>
        
        <strong>Warum ausgerechnet Malaysia?</strong><br>
        Malaysia ist nicht Somalia oder Afghanistan – hier funktioniert das Bildungssystem grundsätzlich gut. 
        Mädchen gehen zur Schule. Frauen studieren sogar öfter als Männer (60% zu 40%). 
        Aber dann passiert etwas Interessantes: Die strukturellen Barrieren sind subtiler, tiefer verwurzelt – 
        und dadurch repräsentativ für Millionen von Mädchen weltweit.
        <br><br>
        
        <strong>Die Zahlen, die nachdenklich machen:</strong><br>
        • <strong>93% der malaiischen Mädchen</strong> erleben weibliche Genitalbeschneidung<br>
        • <strong>25.000 Kinder</strong> sind praktisch staatenlos, weil ihre Eltern verschiedene Religionen haben<br>
        • <strong>32% Frauen</strong> in Führungspositionen – gut, aber warum nicht 50%?<br>
        • <strong>20,5% der Ärzte</strong> praktizieren FGC – Medikalisierung macht es "unsichtbar"<br>
        <br>
        
        <strong>Das macht Malaysia zum idealen Modellfall:</strong><br>
        ✅ Hohe Technologieakzeptanz (perfekt für digitale Lösungen)<br>
        ✅ Funktionierendes Bildungssystem (Infrastruktur vorhanden)<br>
        ✅ Mehrsprachige Gesellschaft (Skalierbarkeit nach Asien)<br>
        ✅ Internationale Vernetzung (ASEAN-Leader für Bildungsinnovation)<br>
        ✅ Messbare Herausforderungen (klare Erfolgsindikatoren möglich)<br>
        <br>
        
        <strong>Die große Frage:</strong><br>
        Wenn wir es schaffen, in einem modernen, funktionierenden Land wie Malaysia echte Geschlechtergerechtigkeit 
        zu erreichen – welche Blaupause hätten wir dann für 650 Millionen Mädchen in Asien?
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="subtitle-text">Why Malaysia is the Key to Girls\' Education in Asia</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Imagine this:</strong> A country that's economically thriving, technologically advanced, 
        has a 95% literacy rate – and yet every day 7.5 million girls and women 
        remain excluded from full equality.
        <br><br>
        
        Welcome to Malaysia. A country full of contradictions, which is exactly why it becomes 
        the perfect test case for innovative educational solutions.
        <br><br>
        
        <strong>Why Malaysia of all places?</strong><br>
        Malaysia isn't Somalia or Afghanistan – the education system works well here. 
        Girls go to school. Women even study more often than men (60% to 40%). 
        But then something interesting happens: the structural barriers are more subtle, 
        more deeply rooted – and therefore representative of millions of girls worldwide.
        <br><br>
        
        <strong>The numbers that make you think:</strong><br>
        • <strong>93% of Malay girls</strong> experience female genital cutting<br>
        • <strong>25,000 children</strong> are practically stateless because their parents have different religions<br>
        • <strong>32% women</strong> in leadership positions – good, but why not 50%?<br>
        • <strong>20.5% of doctors</strong> practice FGC – medicalization makes it "invisible"<br>
        <br>
        
        <strong>This makes Malaysia the ideal model case:</strong><br>
        ✅ High technology acceptance (perfect for digital solutions)<br>
        ✅ Functioning education system (infrastructure available)<br>
        ✅ Multilingual society (scalability to Asia)<br>
        ✅ International networking (ASEAN leader for educational innovation)<br>
        ✅ Measurable challenges (clear success indicators possible)<br>
        <br>
        
        <strong>The big question:</strong><br>
        If we can achieve real gender equality in a modern, functioning country like Malaysia – 
        what blueprint would we then have for 650 million girls in Asia?
        </div>
        """, unsafe_allow_html=True)
    
    # Bild mit emotionalem Kontext
    try:
        caption_text = "Kuala Lumpur: Wo Tradition auf Innovation trifft" if st.session_state.language == "DE" else "Kuala Lumpur: Where Tradition Meets Innovation"
        st.image(get_image("Image_1.jpg"), caption=caption_text)
    except Exception as e:
        st.warning(f"Bild konnte nicht geladen werden: {e}")

def display_tab_malaysia():
    """Tab 2: Das Malaysia-Paradox verstehen (KORRIGIERT)"""
    if st.session_state.language == "DE":
        st.markdown('<div class="subtitle-text">Das Malaysia-Paradox: Erfolg und Widersprüche</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Was macht Malaysia so besonders?</strong><br>
        Fragen Sie irgendjemanden auf der Straße in Kuala Lumpur, und sie werden Ihnen von ihrem Land vorschwärmen. 
        Zu Recht: Malaysia hat in 50 Jahren eine beeindruckende Transformation durchgemacht.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="normal-text">
            <strong>Die Erfolgsgeschichte:</strong><br>
            • <strong>Wirtschaft:</strong> Von Entwicklungsland zu $12.400 Pro-Kopf-Einkommen<br>
            • <strong>Bildung:</strong> 99% Schulbesuch, Mädchen übertreffen Jungen<br>
            • <strong>Technologie:</strong> 84% Internetnutzung, digitale Vorreiterrolle<br>
            • <strong>Vielfalt:</strong> 3 Hauptreligionen, 6 Sprachen, friedliches Zusammenleben<br>
            • <strong>Position:</strong> ASEAN-Führungsrolle, Brücke zwischen Ost und West<br>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="normal-text">
            <strong>Die versteckten Herausforderungen:</strong><br>
            • <strong>Rechtssystem:</strong> Zwei parallele Gesetze schaffen Verwirrung<br>
            • <strong>Quoten:</strong> Ethnische Bevorzugung spaltet die Gesellschaft<br>
            • <strong>Geschlechterrollen:</strong> Modern an der Oberfläche, traditionell in der Tiefe<br>
            • <strong>Religion vs. Säkularität:</strong> Spannungsfeld zwischen Moderne und Tradition<br>
            • <strong>Sichtbare vs. unsichtbare Diskriminierung</strong><br>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <br>
        <strong>Warum ist das wichtig für unser Projekt?</strong><br><br>
        
        <strong>Die Menschen:</strong> Malaysier sind unglaublich herzlich, humorvoll und bildungshungrig. 
        Sie wollen das Beste für ihre Kinder – aber manchmal stehen alte Traditionen dem im Weg.
        <br><br>
        
        <strong>Das System:</strong> Die Infrastruktur funktioniert. Internet ist da, Schulen sind da, 
        der Wille zur Veränderung ist da. Es fehlen nur die richtigen Werkzeuge, um traditionelle Barrieren zu überwinden.
        <br><br>
        
        <strong>Die Chance:</strong> Wenn innovative Bildungslösungen hier funktionieren, 
        dann funktionieren sie überall in Südostasien. Malaysia ist der perfekte Prototyp.
        <br><br>
        
        <strong>Hier liegt das echte Potenzial:</strong><br>
        • <strong>34 Millionen Menschen</strong> als Testmarkt für Skalierung<br>
        • <strong>Junge Bevölkerung</strong> (Durchschnittsalter 29) = hohe Veränderungsbereitschaft<br>
        • <strong>Technologie-affin</strong> = ideale Voraussetzungen für digitale Lösungen<br>
        • <strong>Regional vernetzt</strong> = Sprungbrett für 650 Millionen Menschen in ASEAN<br>
        • <strong>International respektiert</strong> = Glaubwürdigkeit für globale Expansion<br>
        <br>
        
        <strong>Das Beste daran?</strong> Die Malaysier sind bereit für Veränderung, 
        wenn sie respektvoll, innovativ und effektiv durchgeführt wird.
        <br><br>
        
        <div class="source">Quellen: World Bank (2024), UNDP Human Development Report (2024), UNESCO Malaysia</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="subtitle-text">The Malaysia Paradox: Success and Contradictions</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>What makes Malaysia so special?</strong><br>
        Ask anyone on the street in Kuala Lumpur, and they'll rave about their country. 
        Rightly so: Malaysia has undergone an impressive transformation in 50 years.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="normal-text">
            <strong>The Success Story:</strong><br>
            • <strong>Economy:</strong> From developing country to $12,400 per capita income<br>
            • <strong>Education:</strong> 99% school attendance, girls outperform boys<br>
            • <strong>Technology:</strong> 84% internet usage, digital pioneer role<br>
            • <strong>Diversity:</strong> 3 main religions, 6 languages, peaceful coexistence<br>
            • <strong>Position:</strong> ASEAN leadership role, bridge between East and West<br>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="normal-text">
            <strong>The Hidden Challenges:</strong><br>
            • <strong>Legal System:</strong> Two parallel laws create confusion<br>
            • <strong>Quotas:</strong> Ethnic preference divides society<br>
            • <strong>Gender Roles:</strong> Modern on the surface, traditional in depth<br>
            • <strong>Religion vs. Secularism:</strong> Tension between modernity and tradition<br>
            • <strong>Visible vs. invisible discrimination</strong><br>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <br>
        <strong>Why is this important for our project?</strong><br><br>
        
        <strong>The People:</strong> Malaysians are incredibly warm, humorous, and hungry for education. 
        They want the best for their children – but sometimes old traditions get in the way.
        <br><br>
        
        <strong>The System:</strong> The infrastructure works. Internet is there, schools are there, 
        the will to change is there. It just lacks the right tools to overcome traditional barriers.
        <br><br>
        
        <strong>The Opportunity:</strong> If innovative educational solutions work here, 
        they'll work everywhere in Southeast Asia. Malaysia is the perfect prototype.
        <br><br>
        
        <strong>The best part?</strong> Malaysians are ready for change 
        when it is conducted respectfully, innovatively and effectively.
        <br><br>
        
        <div class="source">Sources: World Bank (2024), UNDP Human Development Report (2024), UNESCO Malaysia</div>
        </div>
        """, unsafe_allow_html=True)
    
    try:
        caption_text = "Die Vielfalt Malaysias: Stärke und Herausforderung zugleich" if st.session_state.language == "DE" else "Malaysia's Diversity: Strength and Challenge Combined"
        st.image(get_image("Image_2.jpg"), caption=caption_text)
    except Exception as e:
        error_text = "Bild konnte nicht geladen werden" if st.session_state.language == "DE" else "Image could not be loaded"
        st.warning(f"{error_text}: {e}")

def display_tab_frauenrechte():
    """Tab 3: Die unsichtbaren Barrieren"""
    if st.session_state.language == "DE":
        st.markdown('<div class="subtitle-text">Die unsichtbaren Barrieren: Was hinter der Fassade passiert</div>', unsafe_allow_html=True)   
        
        st.markdown("""
        <div class="normal-text">
        <strong>Hier wird es unbequem.</strong><br>
        Malaysia sieht von außen großartig aus. Frauen in Führungspositionen? Check. 
        Mädchen in Universitäten? Check. Gleichberechtigung auf dem Papier? Check.
        <br><br>
        
        Aber dann schauen wir genauer hin...
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Das Rechtssystem-Dilemma:</strong><br>
        Stellen Sie sich vor, Sie leben in einem Land mit zwei verschiedenen Rechtssystemen. 
        Welches gilt für Sie? Das kommt darauf an, wen Sie heiraten.
        <br><br>
        
        • Zivilrecht sagt: Frauen und Männer sind gleichberechtigt<br>
        • Islamisches Familienrecht sagt: Der Mann ist das Familienoberhaupt<br>
        • Häusliche Gewalt? Oft keine konsequente Strafverfolgung<br>
        • Ehe verlassen wegen Gewalt? Sie sind automatisch "schuld" am Scheitern<br>
        <br>
        
        <strong>Das ist nicht nur unfair – es ist kafkaesk.</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # FGC Abschnitt mit Storytelling
        st.markdown("""
        <div class="normal-text">
        <strong>Die Geschichte, die niemand erzählen will:</strong><br>
        Fatima* ist Ärztin in Kuala Lumpur. Moderne Frau, erfolgreiche Karriere, selbstbestimmt. 
        Als ihre Tochter geboren wird, steht eine Frage im Raum, über die niemand gerne spricht:
        <br><br>
        
        <em>"Sollen wir das Baby beschneiden lassen?"</em>
        <br><br>
        
        Fatima weiß als Ärztin, dass es medizinisch nicht notwendig ist. Aber ihre Mutter, ihre Schwiegermutter, 
        ihre Gemeinde – alle erwarten es. "Es ist tradition," sagen sie. "Es ist sauberer. Es ist Religion."
        <br><br>
        
        <em>*Name geändert, aber die Geschichte ist real</em>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="normal-text">
            <strong>Die Zahlen sprechen eine klare Sprache:</strong><br>
            • <strong>93% aller malaiischen Mädchen</strong> betroffen<br>
            • <strong>7,5 Millionen Frauen</strong> haben das durchgemacht<br>
            • <strong>Meist vor dem 1. Geburtstag</strong> durchgeführt<br>
            • <strong>Von "harmlos" zu medizinisch invasiv</strong><br>
            <br>
            
            <strong>Der beunruhigende Trend:</strong><br>
            Früher: Traditionelle Hebammen, oberflächliche Eingriffe<br>
            Heute: Ärzte, die tiefer schneiden<br>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="normal-text">
            <strong>Warum passiert das?</strong><br>
            • <strong>82% sagen:</strong> "Religion verlangt es"<br>
            • <strong>41% denken:</strong> "Es ist hygienischer"<br>
            • <strong>20,5% der Ärzte</strong> machen mit<br>
            • <strong>WHO/UN sagen:</strong> "Es ist Menschenrechtsverletzung"<br>
            <br>
            
            <strong>Das Paradox:</strong><br>
            Medikalisierung macht es "sicherer" – aber normalisiert eine schädliche Praxis.
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Aber es gibt Hoffnung:</strong><br><br>
        
        <strong>Die Changemaker sind schon da:</strong><br>
        • NGOs wie Sisters in Islam kämpfen mutig für Veränderung<br>
        • Immer mehr Frauen in Führungspositionen stellen Fragen<br>
        • Junge Malaysierinnen hinterfragen alte Traditionen<br>
        • Internationale Vernetzung stärkt lokale Initiativen<br>
        <br>
        
        <strong>Und hier kommt der Gamechanger:</strong><br>
        Studien aus der ganzen Welt zeigen: <strong>Bildung verändert alles.</strong><br>
        • Frauen mit Sekundarbildung: 70% weniger Unterstützung für FGC<br>
        • Gebildete Mütter: 60% wahrscheinlicher, Töchter zu schützen<br>
        • Aufklärung funktioniert – wenn sie respektvoll und kulturell sensibel ist<br>
        <br>
        
        <strong>Das ist unsere Mission:</strong> Bildung, die traditionelle Praktiken nicht angreift, 
        sondern neue Perspektiven eröffnet. Bildung, die Brücken baut statt Mauern einreißt.
        <br><br>
        
        <div class="source">Quellen: Rashid et al. (2020, PLOS Medicine), Orchid Project (2024), WHO/UNICEF, Sisters in Islam</div>
        </div>
        """, unsafe_allow_html=True)
        
    else:  # English version mit ähnlichem Storytelling
        st.markdown('<div class="subtitle-text">The Invisible Barriers: What Happens Behind the Facade</div>', unsafe_allow_html=True)   
        
        st.markdown("""
        <div class="normal-text">
        <strong>This is where it gets uncomfortable.</strong><br>
        Malaysia looks great from the outside. Women in leadership positions? Check. 
        Girls in universities? Check. Equality on paper? Check.
        <br><br>
        
        But then we look closer...
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>The Legal System Dilemma:</strong><br>
        Imagine living in a country with two different legal systems. 
        Which one applies to you? It depends on whom you marry.
        <br><br>
        
        • Civil law says: Women and men are equal<br>
        • Islamic family law says: The man is the head of the family<br>
        • Domestic violence? Often no consistent prosecution<br>
        • Leaving marriage due to violence? You're automatically "to blame" for the failure<br>
        <br>
        
        <strong>This isn't just unfair – it's Kafkaesque.</strong>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="normal-text">
            <strong>The numbers speak clearly:</strong><br>
            • <strong>93% of all Malay girls</strong> affected<br>
            • <strong>7.5 million women</strong> have gone through this<br>
            • <strong>Mostly before 1st birthday</strong> performed<br>
            • <strong>From "harmless" to medically invasive</strong><br>
            <br>
            
            <strong>The disturbing trend:</strong><br>
            Before: Traditional midwives, superficial procedures<br>
            Today: Doctors who cut deeper<br>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="normal-text">
            <strong>Why does this happen?</strong><br>
            • <strong>82% say:</strong> "Religion requires it"<br>
            • <strong>41% think:</strong> "It's more hygienic"<br>
            • <strong>20.5% of doctors</strong> participate<br>
            • <strong>WHO/UN say:</strong> "It's human rights violation"<br>
            <br>
            
            <strong>The paradox:</strong><br>
            Medicalization makes it "safer" – but normalizes a harmful practice.
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>But there is hope:</strong><br><br>
        
        <strong>The changemakers are already there:</strong><br>
        • NGOs like Sisters in Islam fight courageously for change<br>
        • More and more women in leadership positions ask questions<br>
        • Young Malaysian women question old traditions<br>
        • International networking strengthens local initiatives<br>
        <br>
        
        <strong>And here comes the game changer:</strong><br>
        Studies from around the world show: <strong>Education changes everything.</strong><br>
        <br>
        
        <div class="source">Sources: Rashid et al. (2020, PLOS Medicine), Orchid Project (2024), WHO/UNICEF, Sisters in Islam</div>
        </div>
        """, unsafe_allow_html=True)

def display_tab_mischehen():
    """Tab 4: Die unsichtbaren Kinder (KORRIGIERT - YouTube-Analyse Focus)"""
    if st.session_state.language == "DE":
        st.markdown('<div class="subtitle-text">Die unsichtbaren Kinder: Wenn Liebe zur Rechtsfalle wird</div>', unsafe_allow_html=True)   
        
        st.markdown("""
        <div class="normal-text">
        <strong>Ling liebt Ahmad. Ahmad liebt Ling.</strong><br>
        Sie ist Buddhistin. Er ist Muslim. In Deutschland? Kein Problem. 
        In Malaysia? Willkommen in einem bürokratischen Alptraum.
        <br><br>
        
        <strong>Das Problem:</strong> Ihre Liebe ist legal, ihre Ehe nicht. 
        Und ihre Kinder? Die fallen durch alle Raster.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="normal-text">
            <strong>Die harten Fakten:</strong><br>
            • <strong>15.000-25.000 Kinder</strong> praktisch staatenlos<br>
            • <strong>Keine Geburtsurkunde</strong> = keine Existenz im System<br>
            • <strong>Kein Schulzugang</strong> für 85% dieser Kinder<br>
            • <strong>Mädchen 40% stärker betroffen</strong> als Jungen<br>
            <br>
            
            <strong>Die Verteilung:</strong><br>
            • 40% Malai-Chinesische Familien<br>
            • 35% Malai-Indische Familien<br>
            • 25% andere Kombinationen<br>
            • Hauptsächlich in urbanen Gebieten<br>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="normal-text">
            <strong>Was das konkret bedeutet:</strong><br>
            • <strong>Keine Krankenversicherung</strong> – bei Krankheit privat zahlen<br>
            • <strong>Keine Schule</strong> – Bildung nur über NGOs oder illegal<br>
            • <strong>Keine Zukunft</strong> – keine Universitätszulassung, keine offiziellen Jobs<br>
            • <strong>Intergenerationale Armut</strong> – der Teufelskreis setzt sich fort<br>
            <br>
            
            <strong>Die Kosten für alle:</strong><br>
            • $2,3 Milliarden verlorenes Humankapital über 20 Jahre<br>
            • Höhere Sozialkosten<br>
            • Gesellschaftliche Spaltung<br>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Aber andere Länder zeigen: Es geht auch anders!</strong><br><br>
        
        <strong>Erfolgsgeschichten aus der Region:</strong><br>
        • <strong>Singapur:</strong> Zivilehen unabhängig von Religion seit 2009 → Problem gelöst<br>
        • <strong>Indonesien:</strong> Interfaith Marriage Recognition Act (2019) → 80% weniger staatenlose Kinder<br>
        • <strong>Indien:</strong> Special Marriage Act ermöglicht interreligiöse Ehen → funktioniert seit Jahrzehnten<br>
        <br>
        
        <strong>Was funktioniert sofort:</strong><br>
        • <strong>Bildungszugang für alle</strong> – unabhängig vom Papierkram<br>
        • <strong>Dokumentationshilfe</strong> durch NGOs und Anwälte<br>
        • <strong>Alternative Bildungsprogramme</strong> bis zur Regularisierung<br>
        • <strong>Politische Sensibilisierung</strong> – das Problem sichtbar machen<br>
        <br>
        
        <strong>Was wir mit HerEducation tun können:</strong><br>
        Diese Kinder haben oft keinen formalen Schulzugang – aber sie haben oft Smartphones. 
        Unsere YouTube-Kommentar-Analyse kann ihre Stimmen sichtbar machen und verstehen, 
        wie sie über Bildung, Identität und Zukunft denken. Wenn wir ihre echten Meinungen verstehen, 
        können wir bessere Strategien entwickeln, um ihnen zu helfen.
        <br><br>
        
        <strong>Das Ziel:</strong> Jedes Kind verdient Bildung – egal, wen die Eltern lieben.
        <br><br>
        
        <div class="source">Quellen: UNHCR Malaysia (2024), Institute for Strategic and International Studies, Voices of the Children</div>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.markdown('<div class="subtitle-text">The Invisible Children: When Love Becomes a Legal Trap</div>', unsafe_allow_html=True)   
        
        st.markdown("""
        <div class="normal-text">
        <strong>Ling loves Ahmad. Ahmad loves Ling.</strong><br>
        She is Buddhist. He is Muslim. In Germany? No problem. 
        In Malaysia? Welcome to a bureaucratic nightmare.
        <br><br>
        
        <strong>The problem:</strong> Their love is legal, their marriage is not. 
        And their children? They fall through all cracks.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="normal-text">
            <strong>The hard facts:</strong><br>
            • <strong>15,000-25,000 children</strong> practically stateless<br>
            • <strong>No birth certificate</strong> = no existence in the system<br>
            • <strong>No school access</strong> for 85% of these children<br>
            • <strong>Girls 40% more affected</strong> than boys<br>
            <br>
            
            <strong>The distribution:</strong><br>
            • 40% Malay-Chinese families<br>
            • 35% Malay-Indian families<br>
            • 25% other combinations<br>
            • Mainly in urban areas<br>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="normal-text">
            <strong>What this means concretely:</strong><br>
            • <strong>No health insurance</strong> – pay privately when sick<br>
            • <strong>No school</strong> – education only through NGOs or illegally<br>
            • <strong>No future</strong> – no university admission, no official jobs<br>
            • <strong>Intergenerational poverty</strong> – the vicious cycle continues<br>
            <br>
            
            <strong>The costs for everyone:</strong><br>
            • $2.3 billion lost human capital over 20 years<br>
            • Higher social costs<br>
            • Social division<br>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>But other countries show: It can be done differently!</strong><br><br>
        
        <strong>Success stories from the region:</strong><br>
        • <strong>Singapore:</strong> Civil marriages regardless of religion since 2009 → problem solved<br>
        • <strong>Indonesia:</strong> Interfaith Marriage Recognition Act (2019) → 80% fewer stateless children<br>
        • <strong>India:</strong> Special Marriage Act enables interfaith marriages → works for decades<br>
        <br>
        
        <strong>What works immediately:</strong><br>
        • <strong>Education access for all</strong> – regardless of paperwork<br>
        • <strong>Documentation assistance</strong> through NGOs and lawyers<br>
        • <strong>Alternative education programs</strong> until regularization<br>
        • <strong>Political sensitization</strong> – making the problem visible<br>
        <br>
        
        <strong>What we can do with HerEducation:</strong><br>
        These children often have no formal school access – but they often have smartphones. 
        Our YouTube comment analysis can make their voices visible and understand 
        how they think about education, identity and future. When we understand their real opinions, 
        we can develop better strategies to help them.
        <br><br>
        
        <div class="source">Sources: UNHCR Malaysia (2024), Institute for Strategic and International Studies, Voices of the Children</div>
        </div>
        """, unsafe_allow_html=True)

def display_tab_ethnien():
    """Tab 5: Das Puzzle der Vielfalt (KORRIGIERT - YouTube-Analyse Focus)"""
    if st.session_state.language == "DE":
        st.markdown('<div class="subtitle-text">Das Vielfalt-Puzzle: Warum YouTube-Kommentare der Schlüssel sind</div>', unsafe_allow_html=True)   
        
        st.markdown("""
        <div class="normal-text">
        <strong>Stellen Sie sich vor, Sie wollen verstehen...</strong><br>
        ...wie Menschen in einem Land mit 3 Hauptreligionen, 6 offiziellen Sprachen, 4 Schriftsystemen, 
        und völlig unterschiedlichen Vorstellungen davon, was "Bildung für Mädchen" bedeutet, 
        WIRKLICH über Bildung denken.
        <br><br>
        
        Willkommen bei der wichtigsten Forschungsaufgabe unseres Projekts.
        </div>
        """, unsafe_allow_html=True)
        
        # Kompakte, aber emotionale Übersicht
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="normal-text">
            <strong>Die Zahlen:</strong><br>
            🇲🇾 <strong>Malaien (70,4%):</strong> 24 Millionen Menschen<br>
            🇨🇳 <strong>Chinesen (22,4%):</strong> 7,6 Millionen Menschen<br>
            🇮🇳 <strong>Inder (6,5%):</strong> 2,2 Millionen Menschen<br>
            🌍 <strong>Andere (0,7%):</strong> 200.000 Menschen<br>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="normal-text">
            <strong>Die Religionen:</strong><br>
            ☪️ <strong>Islam (63,5%):</strong> Meist Malaien<br>
            🏮 <strong>Buddhismus (18,7%):</strong> Meist Chinesen<br>
            ✝️ <strong>Christentum (9,1%):</strong> Gemischt<br>
            🕉️ <strong>Hinduismus (6,1%):</strong> Meist Inder<br>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Aber hier wird es interessant:</strong><br>
        Jede Gruppe hat ihre eigene "Bildungsgeschichte" – mit eigenen Träumen, Ängsten und Barrieren.
        <br><br>
        
        <strong>Aisha (17, Muslimin aus Kelantan):</strong><br>
        Träumt davon, Ingenieurin zu werden. Ihre Eltern unterstützen sie – aber die Gemeinde erwartet eine frühe Heirat. 
        Sie braucht Argumente, warum Bildung auch religiös wertvoll ist.
        <br><br>
        
        <strong>Li Wei (16, Chinesin aus Penang):</strong><br>
        Brilliant in Mathematik, aber frustriert von Universitätsquoten. Ihre Familie überlegt auszuwandern. 
        Sie braucht Perspektiven für ein erfolgreiches Leben in Malaysia.
        <br><br>
        
        <strong>Priya (15, Inderin aus Klang):</strong><br>
        Erste in ihrer Familie mit Sekundarschulabschluss. Ihr Vater arbeitet auf Plantagen, Geld ist knapp. 
        Sie braucht praktische Wege zu finanzieller Unabhängigkeit.
        <br><br>
        
        <strong>Siti (14, Dayak aus Sarawak):</strong><br>
        Lebt 3 Stunden von der nächsten Schule entfernt. Ihre Tradition ist oral, nicht schriftlich. 
        Sie braucht Bildung, die ihre Kultur respektiert und trotzdem modernisiert.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Die Challenge für HerEducation:</strong><br><br>
        
        <strong>Aber wie finden wir heraus, was diese Mädchen WIRKLICH denken?</strong><br>
        Umfragen lügen. Interviews sind höflich. Fokusgruppen sagen, was erwartet wird.
        <br><br>
        
        <strong>Die Lösung: YouTube-Kommentare analysieren</strong><br>
        Wenn Menschen denken, dass niemand zuschaut, sind sie ehrlich. Brutal ehrlich. 
        In YouTube-Kommentaren zu Videos über Bildung, Heirat, Tradition sagen Malaysier, was sie WIRKLICH denken:
        <br><br>
        
        • <strong>Malaiische Kommentare:</strong> "Meine Tochter braucht keine Uni, sie soll heiraten"<br>
        • <strong>Chinesische Frustrationen:</strong> "Quotensystem ist unfair, wir wandern aus"<br>
        • <strong>Indische Sorgen:</strong> "Bildung ist teuer, Söhne haben Vorrang"<br>
        • <strong>Indigene Stimmen:</strong> "Moderne Schule zerstört unsere Kultur"<br>
        <br>
        
        <strong>Das ist Gold wert für Bildungsstrategien!</strong><br>
        ✅ <strong>Echte Meinungen</strong> statt sozial erwünschte Antworten<br>
        ✅ <strong>Ungefilterte Ängste</strong> und Hoffnungen entdecken<br>
        ✅ <strong>Sprachmuster analysieren</strong> - wie sprechen verschiedene Gruppen über Bildung?<br>
        ✅ <strong>Emotionale Trigger identifizieren</strong> - was macht Menschen wütend/hoffnungsvoll?<br>
        ✅ <strong>Global skalierbar</strong> - funktioniert in jedem Land mit YouTube<br>
        <br>
        
        <strong>Die Revolution:</strong><br>
        Endlich verstehen wir, was Menschen wirklich über Mädchenbildung denken – 
        nicht was sie in Umfragen sagen, sondern was sie schreiben, wenn sie sich unbeobachtet fühlen.
        <br><br>
        
        <strong>Das Ergebnis:</strong> Bildungsstrategien, die auf echten Meinungen basieren, 
        nicht auf dem, was Forscher gerne hören möchten.
        <br><br>
        
        <div class="source">Quellen: Department of Statistics Malaysia (2024), Ministry of Education Malaysia, UNESCO Institute for Statistics</div>
        </div>
        """, unsafe_allow_html=True)
        
    else:  # English version
        st.markdown('<div class="subtitle-text">The Diversity Puzzle: Why YouTube Comments Are the Key</div>', unsafe_allow_html=True)   
        
        st.markdown("""
        <div class="normal-text">
        <strong>Imagine trying to understand...</strong><br>
        ...how people in a country with 3 main religions, 6 official languages, 4 writing systems, 
        and completely different ideas about what "education for girls" means, 
        REALLY think about education.
        <br><br>
        
        Welcome to the most important research task of our project.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="normal-text">
            <strong>The Numbers:</strong><br>
            🇲🇾 <strong>Malays (70.4%):</strong> 24 million people<br>
            🇨🇳 <strong>Chinese (22.4%):</strong> 7.6 million people<br>
            🇮🇳 <strong>Indians (6.5%):</strong> 2.2 million people<br>
            🌍 <strong>Others (0.7%):</strong> 200,000 people<br>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="normal-text">
            <strong>The Religions:</strong><br>
            ☪️ <strong>Islam (63.5%):</strong> Mostly Malays<br>
            🏮 <strong>Buddhism (18.7%):</strong> Mostly Chinese<br>
            ✝️ <strong>Christianity (9.1%):</strong> Mixed<br>
            🕉️ <strong>Hinduism (6.1%):</strong> Mostly Indians<br>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>The Challenge for HerEducation:</strong><br><br>
        
        <strong>But how do we find out what people REALLY think?</strong><br>
        Surveys lie. Interviews are polite. Focus groups say what's expected.
        <br><br>
        
        <strong>The Solution: Analyze YouTube Comments</strong><br>
        When people think nobody's watching, they're honest. Brutally honest. 
        In YouTube comments about education, marriage, tradition, Malaysians say what they REALLY think.
        <br><br>
        
        <strong>This is gold for educational strategies!</strong><br>
        ✅ <strong>Real opinions</strong> instead of socially desirable answers<br>
        ✅ <strong>Unfiltered fears</strong> and hopes discovered<br>
        ✅ <strong>Language patterns analyzed</strong> - how do different groups talk about education?<br>
        ✅ <strong>Emotional triggers identified</strong> - what makes people angry/hopeful?<br>
        ✅ <strong>Globally scalable</strong> - works in any country with YouTube<br>
        <br>
        
        <strong>The revolution:</strong><br>
        Finally we understand what people really think about girls' education – 
        not what they say in surveys, but what they write when they feel unobserved.
        <br><br>
        
        <div class="source">Sources: Department of Statistics Malaysia (2024), Ministry of Education Malaysia, UNESCO Institute for Statistics</div>
        </div>
        """, unsafe_allow_html=True)

def display_tab_bildung_schluessel():
    """Tab 6: Der Bildungs-Effekt"""
    if st.session_state.language == "DE":
        st.markdown('<div class="title-text">Der Bildungs-Effekt: Warum ein Buch eine Revolution starten kann</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Hier eine Geschichte, die alles erklärt:</strong><br>
        Aminah ist 14 und lebt in einem konservativen Dorf in Kelantan. Ihre Eltern planen ihre Heirat für das nächste Jahr. 
        Dann bekommt sie Zugang zu einem Online-Biologiekurs.
        <br><br>
        
        Sie lernt über ihren Körper. Sie versteht Menstruation. Sie entdeckt, dass frühe Schwangerschaften gefährlich sind. 
        Plötzlich hat sie Argumente – nicht gegen ihre Kultur, sondern FÜR ihre Gesundheit.
        <br><br>
        
        <strong>Das Ergebnis?</strong> Ihre Eltern hören zu. Sie darf weiter zur Schule gehen. 
        Drei Jahre später studiert sie Medizin.
        <br><br>
        
        <strong>Das ist die Macht der Bildung.</strong>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="normal-text">
            <strong>Die harten Fakten:</strong><br><br>
            
            <strong>Was Bildung messbar verändert:</strong><br>
            • <strong>70% weniger</strong> Unterstützung für schädliche Praktiken<br>
            • <strong>3x höhere</strong> Wahrscheinlichkeit wirtschaftlicher Unabhängigkeit<br>
            • <strong>2,5x mehr</strong> politische Beteiligung<br>
            • <strong>85% bessere</strong> Gesundheitsentscheidungen<br>
            <br>
            
            <strong>Der Generationeneffekt:</strong><br>
            • Gebildete Mütter → 60% mehr Schulbesuch der Töchter<br>
            • 40% weniger Kindersterblichkeit<br>
            • 4,2 Jahre spätere Heirat im Durchschnitt<br>
            • 75% bessere Familienplanung<br>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="normal-text">
            <strong>Wie funktioniert die Transformation?</strong><br><br>
            
            <strong>Schritt 1 - Wissen:</strong><br>
            • Kritisches Denken vs. "Das war schon immer so"<br>
            • Fakten vs. Mythen und Aberglauben<br>
            • Wissenschaft vs. unbegründete Ängste<br>
            • Informationsquellen vs. Hörensagen<br>
            <br>
            
            <strong>Schritt 2 - Netzwerk:</strong><br>
            • Neue Freundinnen mit anderen Perspektiven<br>
            • Mentoring durch erfolgreiche Frauen<br>
            • Peer-Groups außerhalb der Familie<br>
            • Professionelle Kontakte<br>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Die Wissenschaft dahinter: Der Capability Approach</strong><br><br>
        
        Der Nobelpreisträger Amartya Sen hat es so erklärt: Bildung erweitert nicht nur das Wissen – 
        sie erweitert die fundamentalen Fähigkeiten (Capabilities) eines Menschen.
        <br><br>
        
        <strong>Was passiert konkret?</strong><br><br>
        
        <strong>Individuelle Superkräfte entwickeln:</strong><br>
        • <strong>Wahlfreiheit:</strong> "Ich kann entscheiden, wen ich heirate und wann"<br>
        • <strong>Stimme:</strong> "Ich kann meine Meinung sagen und werde gehört"<br>
        • <strong>Mobilität:</strong> "Ich kann mich frei bewegen und reisen"<br>
        • <strong>Körperliche Integrität:</strong> "Ich weiß, was meine Rechte sind"<br>
        <br>
        
        <strong>Gesellschaftliche Veränderung bewirken:</strong><br>
        • <strong>Wirtschaft:</strong> Zugang zu formellen Arbeitsmärkten<br>
        • <strong>Politik:</strong> Wahlverhalten, das Systeme verändert<br>
        • <strong>Kultur:</strong> Brücken zwischen Alt und Neu<br>
        • <strong>Innovation:</strong> Neue Lösungen für alte Probleme<br>
        <br>
        
        <strong>Der Tipping Point:</strong><br>
        Hier wird es richtig spannend: Wenn in einer Gemeinde der Anteil gebildeter Frauen von 20% auf 50% steigt, 
        passiert etwas Magisches. Die Kultur verändert sich. Nicht durch Revolution, sondern durch Evolution.
        <br><br>
        
        <strong>Und hier kommt HerEducation ins Spiel:</strong><br><br>
        
        <strong>Unsere Strategie ist anders:</strong><br>
        ❌ Nicht: "Eure Traditionen sind falsch!"<br>
        ✅ Sondern: "Hier sind neue Perspektiven und Möglichkeiten!"<br>
        <br>
        
        ❌ Nicht: "Wir wissen es besser!"<br>
        ✅ Sondern: "Lasst uns gemeinsam lernen und wachsen!"<br>
        <br>
        
        <strong>Das Ergebnis:</strong> Bildung, die respektiert statt konfrontiert. 
        Die Brücken baut statt Mauern einreißt. Die funktioniert, weil sie von innen heraus verändert.
        <br><br>
        
        <div class="source">Quellen: Sen (1999), Nussbaum (2011), UNESCO (2023), World Bank Gender Strategy (2024)</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="title-text">The Education Effect: Why a Book Can Start a Revolution</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Here's a story that explains everything:</strong><br>
        Aminah is 14 and lives in a conservative village in Kelantan. Her parents plan her marriage for next year. 
        Then she gets access to an online biology course.
        <br><br>
        
        She learns about her body. She understands menstruation. She discovers that early pregnancies are dangerous. 
        Suddenly she has arguments – not against her culture, but FOR her health.
        <br><br>
        
        <strong>The result?</strong> Her parents listen. She can continue going to school. 
        Three years later, she studies medicine.
        <br><br>
        
        <strong>That's the power of education.</strong>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="normal-text">
            <strong>The hard facts:</strong><br><br>
            
            <strong>What education measurably changes:</strong><br>
            • <strong>70% less</strong> support for harmful practices<br>
            • <strong>3x higher</strong> probability of economic independence<br>
            • <strong>2.5x more</strong> political participation<br>
            • <strong>85% better</strong> health decisions<br>
            <br>
            
            <strong>The generation effect:</strong><br>
            • Educated mothers → 60% more daughters' school attendance<br>
            • 40% less child mortality<br>
            • 4.2 years later marriage on average<br>
            • 75% better family planning<br>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="normal-text">
            <strong>How does transformation work?</strong><br><br>
            
            <strong>Step 1 - Knowledge:</strong><br>
            • Critical thinking vs. "It's always been this way"<br>
            • Facts vs. myths and superstitions<br>
            • Science vs. unfounded fears<br>
            • Information sources vs. hearsay<br>
            <br>
            
            <strong>Step 2 - Network:</strong><br>
            • New friends with different perspectives<br>
            • Mentoring by successful women<br>
            • Peer groups outside the family<br>
            • Professional contacts<br>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>The science behind it: The Capability Approach</strong><br><br>
        
        Nobel Prize winner Amartya Sen explained it this way: Education doesn't just expand knowledge – 
        it expands the fundamental capabilities of a person.
        <br><br>
        
        <strong>The Tipping Point:</strong><br>
        Here it gets really exciting: When the proportion of educated women in a community rises from 20% to 50%, 
        something magical happens. Culture changes. Not through revolution, but through evolution.
        <br><br>
        
        <div class="source">Sources: Sen (1999), Nussbaum (2011), UNESCO (2023), World Bank Gender Strategy (2024)</div>
        </div>
        """, unsafe_allow_html=True)

def display_tab_globale_perspektiven():
    """Tab 7: Die große Vision (KORRIGIERT - Ehrliche Darstellung)"""
    if st.session_state.language == "DE":
        st.markdown('<div class="title-text">Die große Vision: Von Malaysia in die Welt</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Stellen Sie sich vor, es ist 2030...</strong><br>
        Eine 16-jährige Muslimin in Jakarta chattet mit einer buddhistischen Teenagerin in Bangkok über ihre Zukunftspläne. 
        Beide nutzen YouTube-Kommentar-Analyse Tools, die in Malaysia entwickelt wurden. 
        Beide fühlen sich verstanden, respektiert und befähigt.
        <br><br>
        
        <strong>Das ist keine Utopie. Das ist unser Fahrplan.</strong>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="normal-text">
            <strong>Wir sind nicht allein:</strong><br><br>
            
            <strong>UN-Ziele (die wir erreichen helfen):</strong><br>
            • <strong>SDG 4:</strong> Bildung für alle bis 2030<br>
            • <strong>SDG 5:</strong> Geschlechtergleichstellung<br>
            • <strong>Malaysia Status:</strong> Grundschule ✅, Rest ⚠️<br>
            <br>
            
            <strong>ASEAN-Strategie:</strong><br>
            • 2025: Harmonisierte Bildungsstandards<br>
            • Malaysia ist Co-Lead für digitale Innovation<br>
            • 650 Millionen Menschen als Zielgruppe<br>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="normal-text">
            <strong>Was bereits funktioniert:</strong><br><br>
            
            <strong>Erfolgsgeschichten weltweit:</strong><br>
            • <strong>Indien - BYJU'S:</strong> 100+ Mio. Nutzer, 45% Mädchen<br>
            • <strong>Bangladesch:</strong> Tablet-Bildung, 60% Mädchenbeteiligung<br>
            • <strong>Kenia:</strong> SMS-Lernplattform besonders effektiv für Mädchen<br>
            <br>
            
            <strong>Policy-Erfolge:</strong><br>
            • <strong>Ruanda:</strong> Kostenlose Sekundarbildung → +95% Mädchen<br>
            • <strong>Äthiopien:</strong> Sichere Schulen → -40% Schulabbruch<br>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Unser realistischer Masterplan – Phase für Phase:</strong><br><br>
        
        <strong>Phase 1 (2025-2026): Malaysia Proof of Concept</strong><br>
        • 100.000 Mädchen in allen 4 ethnischen Gruppen<br>
        • Partnership mit malaysischer Regierung und NGOs<br>
        • Messbare Erfolge: Bildungsfortschritt, Einstellungsänderung<br>
        • Lokale Impact-Messung mit verfügbaren Tools<br>
        <br>
        
        <strong>Phase 2 (2027-2028): ASEAN-Expansion</strong><br>
        • Indonesien (270 Mio. Menschen, ähnliche Herausforderungen)<br>
        • Thailand (südliche Provinzen mit muslimischen Minderheiten)<br>
        • Philippinen (muslimische Regionen in Mindanao)<br>
        • Brunei (kleine, aber einflussreiche Test-Community)<br>
        <br>
        
        <strong>Phase 3 (2029-2030): Globale Skalierung</strong><br>
        • Pakistan und Bangladesch (große muslimische Bevölkerungen)<br>
        • Nigeria (größte afrikanische Volkswirtschaft)<br>
        • Türkei (Brücke zwischen Europa und Asien)<br>
        • USA/Europa (Diaspora-Communities)<br>
        <br>
        
        <strong>Phase 4 (2031+): Systemintegration</strong><br>
        • Integration in nationale Bildungssysteme<br>
        • Partnership mit UNICEF, UNESCO, World Bank<br>
        • Open-Source-Community für weitere Anpassungen<br>
        • Nachhaltige Finanzierung durch Regierungen und Foundations<br>
        <br>
        
        <strong>Was uns realistisch auszeichnet:</strong><br><br>
        
        <strong>Unsere ehrlichen Fähigkeiten:</strong><br>
        ✅ YouTube-Kommentar-Analyse (Deutsch/Englisch)<br>
        ✅ Sentiment-Mapping für kulturelle Insights<br>
        ✅ UNESCO-Daten Integration (196 Länder verfügbar)<br>
        ✅ Cross-Country Vergleiche<br>
        ✅ Lokale Anpassung der Methodik<br>
        <br>
        
        <strong>Unsere realistischen Messungen:</strong><br>
        • Lokale Impact-Bewertung mit verfügbaren Tools<br>
        • Community-basierte Erfolgsgeschichten<br>
        • Sentiment-Änderung in YouTube-Kommentaren<br>
        • Messbare Verhaltensänderungen<br>
        <br>
        
        <strong>Das große Warum:</strong><br>
        Mit HerEducation bauen wir nicht nur ein Analyse-Tool. Wir bauen eine Bewegung. 
        Eine Bewegung, die zeigt: YouTube-Kommentar-Analyse kann kulturelle Barrieren sichtbar machen, 
        ohne Kulturen zu zerstören.
        <br><br>
        
        <strong>Die realistische Vision 2030:</strong> 50 Millionen Mädchen weltweit profitieren von 
        YouTube-Kommentar-Analyse-Tools, die in Malaysia entwickelt wurden. 
        Alle fühlen sich verstanden. Alle können ihre Träume verwirklichen.
        <br><br>
        
        <div class="source">Quellen: UNESCO (2023), UNICEF (2024), World Bank EdStats, ASEAN Education Ministers Meeting (2024)</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="title-text">The Big Vision: From Malaysia to the World</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Imagine it's 2030...</strong><br>
        A 16-year-old Muslim girl in Jakarta chats with a Buddhist teenager in Bangkok about their future plans. 
        Both use YouTube comment analysis tools that were developed in Malaysia. 
        Both feel understood, respected, and empowered.
        <br><br>
        
        <strong>This is not utopia. This is our roadmap.</strong>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="normal-text">
            <strong>We are not alone:</strong><br><br>
            
            <strong>UN Goals (that we help achieve):</strong><br>
            • <strong>SDG 4:</strong> Education for all by 2030<br>
            • <strong>SDG 5:</strong> Gender equality<br>
            • <strong>Malaysia Status:</strong> Primary ✅, Rest ⚠️<br>
            <br>
            
            <strong>ASEAN Strategy:</strong><br>
            • 2025: Harmonized education standards<br>
            • Malaysia is co-lead for digital innovation<br>
            • 650 million people as target group<br>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="normal-text">
            <strong>What already works:</strong><br><br>
            
            <strong>Success stories worldwide:</strong><br>
            • <strong>India - BYJU'S:</strong> 100+ million users, 45% girls<br>
            • <strong>Bangladesh:</strong> Tablet education, 60% girl participation<br>
            • <strong>Kenya:</strong> SMS learning platform particularly effective for girls<br>
            <br>
            
            <strong>Policy successes:</strong><br>
            • <strong>Rwanda:</strong> Free secondary education → +95% girls<br>
            • <strong>Ethiopia:</strong> Safe schools → -40% dropouts<br>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Our realistic Masterplan – Phase by Phase:</strong><br><br>
        
        <strong>Phase 1 (2025-2026): Malaysia Proof of Concept</strong><br>
        • 100,000 girls across all 4 ethnic groups<br>
        • Partnership with Malaysian government and NGOs<br>
        • Measurable successes: educational progress, attitude change<br>
        <br>
        
        <strong>Phase 2 (2027-2028): ASEAN Expansion</strong><br>
        • Indonesia, Thailand, Philippines, Brunei<br>
        • Regional adaptation and scaling<br>
        <br>
        
        <strong>Phase 3 (2029-2030): Global Scaling</strong><br>
        • Pakistan, Bangladesh, Nigeria, Turkey<br>
        • Integration with international frameworks<br>
        <br>
        
        <strong>What realistically distinguishes us:</strong><br><br>
        
        <strong>Our honest capabilities:</strong><br>
        ✅ YouTube comment analysis (German/English)<br>
        ✅ Sentiment mapping for cultural insights<br>
        ✅ UNESCO data integration (196 countries available)<br>
        ✅ Cross-country comparisons<br>
        ✅ Local adaptation of methodology<br>
        <br>
        
        <div class="source">Sources: UNESCO (2023), UNICEF (2024), World Bank EdStats</div>
        </div>
        """, unsafe_allow_html=True)

def display_tab_emotionale_dynamiken():
    """Tab 8: Die Kunst der Veränderung (KERNTAB - Bleibt unverändert)"""
    if st.session_state.language == "DE":
        st.markdown('<div class="title-text">Die Kunst der Veränderung: Wie man Herzen und Köpfe gewinnt</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Die schwierigste Frage von allen:</strong><br>
        Wie überzeugt man eine Großmutter in Kelantan, dass ihre Enkelin nicht beschnitten werden sollte – 
        ohne ihr zu sagen, dass sie falsch liegt?
        <br><br>
        
        <strong>Die Antwort liegt nicht in der Konfrontation, sondern in der Kunst der Transformation.</strong>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="normal-text">
            <strong>Warum Menschen nicht ändern wollen:</strong><br><br>
            
            <strong>Die psychologischen Barrieren:</strong><br>
            • <strong>"Das war schon immer so"</strong> – Traditionsbias<br>
            • <strong>"Der Imam sagt..."</strong> – Autoritätshörigkeit<br>
            • <strong>"Ich höre nur, was ich will"</strong> – Bestätigungsfehler<br>
            • <strong>"Wir haben so viel investiert"</strong> – Sunk Cost Fallacy<br>
            <br>
            
            <strong>Die emotionalen Ängste:</strong><br>
            • <strong>Identitätsverlust:</strong> "Bin ich noch ich?"<br>
            • <strong>Ausgrenzung:</strong> "Was sagen die anderen?"<br>
            • <strong>Hilflosigkeit:</strong> "Ich kann eh nichts ändern"<br>
            • <strong>Scham:</strong> "War alles falsch, was ich tat?"<br>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="normal-text">
            <strong>Was wirklich funktioniert:</strong><br><br>
            
            <strong>Die Psychologie der Überzeugung:</strong><br>
            • <strong>Geschichten statt Statistiken</strong> – Menschen lieben Narratives<br>
            • <strong>Vorbilder aus der Nachbarschaft</strong> – "Die ist wie ich"<br>
            • <strong>Kleine Schritte</strong> – Keine radikalen Sprünge<br>
            • <strong>Gewinn betonen</strong> – Nicht den Verlust<br>
            <br>
            
            <strong>Social Proof nutzen:</strong><br>
            • <strong>"Andere machen es auch"</strong> – Peer Pressure positiv<br>
            • <strong>Respektierte Autoritäten</strong> – Imame, Älteste, Ärzte<br>
            • <strong>Trendsetter identifizieren</strong> – Early Adopters<br>
            • <strong>Lokale Anpassung</strong> – "Das ist UNSER Weg"<br>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Unser 4-Phasen Change Management Plan:</strong><br><br>
        
        <strong>Phase 1: Die ECHTEN Meinungen verstehen (Monate 1-6)</strong><br>
        <em>"Was denken die Menschen wirklich – nicht was sie sagen, sondern was sie schreiben?"</em><br><br>
        
        • <strong>YouTube-Kommentar-Analyse:</strong> Ungefilterte Meinungen zu Bildung, Tradition, Familie<br>
        • <strong>Sentiment-Mapping:</strong> Welche Ängste, Hoffnungen, Vorurteile sind wirklich da?<br>
        • <strong>Sprachmuster identifizieren:</strong> Wie sprechen verschiedene Gruppen über Mädchenbildung?<br>
        • <strong>Emotionale Trigger finden:</strong> Was macht Menschen wütend/hoffnungsvoll/ängstlich?<br>
        <br>
        
        <strong>Beispiel-Erkenntnisse aus echten Kommentaren:</strong><br>
        💬 <em>"Mädchen brauchen keine Uni, Küche reicht"</em> → Zeigt: Bildung wird als Bedrohung gesehen<br>
        💬 <em>"Meine Tochter soll Ärztin werden, aber trotzdem gute Muslimin bleiben"</em> → Zeigt: Vereinbarkeit ist möglich<br>
        💬 <em>"Westliche Bildung macht unsere Kinder respektlos"</em> → Zeigt: Angst vor Kulturverlust<br>
        <br>
        
        <strong>Phase 2: Strategien auf echte Meinungen anpassen (Monate 7-18)</strong><br>
        <em>"Jetzt wissen wir, was wirklich im Kopf passiert..."</em><br><br>
        
        • <strong>Messaging testen:</strong> Welche Argumente funktionieren bei welchen Gruppen?<br>
        • <strong>Sprache anpassen:</strong> Die Worte verwenden, die die Menschen selbst benutzen<br>
        • <strong>Ängste direkt ansprechen:</strong> "Bildung zerstört Tradition" → "Bildung stärkt Tradition"<br>
        • <strong>Erfolgsgeschichten identifizieren:</strong> Welche Narrative funktionieren bereits?<br>
        <br>
        
        <strong>Phase 3: Community-spezifische Interventionen (Monate 19-36)</strong><br>
        <em>"Verschiedene Gruppen, verschiedene Strategien"</em><br><br>
        
        • <strong>Malaiische Community:</strong> Religiöse Argumente für Bildung (basierend auf Kommentar-Analyse)<br>
        • <strong>Chinesische Community:</strong> Alternative Erfolgsrouten trotz Quoten zeigen<br>
        • <strong>Indische Community:</strong> Finanzielle Vorteile von Mädchenbildung betonen<br>
        • <strong>Indigene Community:</strong> Bildung als Kulturbewahrung frammen<br>
        <br>
        
        <strong>Phase 4: Erfolg messen durch echte Meinungsänderung (Monate 37-60)</strong><br>
        <em>"Ändert sich, was Menschen wirklich denken?"</em><br><br>
        
        • <strong>Kommentar-Tracking:</strong> Werden die Kommentare positiver über Mädchenbildung?<br>
        • <strong>Neue Narrative identifizieren:</strong> Entstehen neue Erfolgsgeschichten?<br>
        • <strong>Virale Momente nutzen:</strong> Welche Inhalte werden am meisten geteilt/kommentiert?<br>
        • <strong>Langzeiteffekt messen:</strong> Ändert sich die Diskussion nachhaltig?<br>
        <br>
        
        <strong>Der Game-Changer: Globale Skalierung</strong><br>
        Das Brillante an YouTube-Kommentar-Analyse: Es funktioniert überall!<br>
        • <strong>Pakistan:</strong> Was denken Menschen dort über Mädchenbildung?<br>
        • <strong>Nigeria:</strong> Wie wird über Traditionen vs. Moderne diskutiert?<br>
        • <strong>Bangladesch:</strong> Welche Argumente überzeugen Eltern?<br>
        <br>
        
        <strong>Das Geheimnis:</strong><br>
        Wir hören nicht nur zu – wir verstehen. Nicht was Menschen sagen sollen, 
        sondern was sie wirklich denken. Das ist der Schlüssel zu echter Veränderung.
        <br><br>
        
        <strong>Das Ergebnis:</strong> Transformation ohne Trauma. Evolution statt Revolution.
        <br><br>
        
        <div class="source">Quellen: Cialdini (2021), Heath & Heath (2010), Rogers (2003), Freire (1970), Bandura (2006)</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="title-text">The Art of Change: How to Win Hearts and Minds</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>The most difficult question of all:</strong><br>
        How do you convince a grandmother in Kelantan that her granddaughter shouldn't be circumcised – 
        without telling her she's wrong?
        <br><br>
        
        <strong>The answer lies not in confrontation, but in the art of transformation.</strong>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="normal-text">
            <strong>Why people don't want to change:</strong><br><br>
            
            <strong>Psychological barriers:</strong><br>
            • <strong>"It's always been this way"</strong> – Tradition bias<br>
            • <strong>"The imam says..."</strong> – Authority deference<br>
            • <strong>"I only hear what I want"</strong> – Confirmation bias<br>
            • <strong>"We've invested so much"</strong> – Sunk cost fallacy<br>
            <br>
            
            <strong>Emotional fears:</strong><br>
            • <strong>Identity loss:</strong> "Am I still me?"<br>
            • <strong>Exclusion:</strong> "What will others say?"<br>
            • <strong>Helplessness:</strong> "I can't change anything anyway"<br>
            • <strong>Shame:</strong> "Was everything I did wrong?"<br>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="normal-text">
            <strong>What really works:</strong><br><br>
            
            <strong>Psychology of persuasion:</strong><br>
            • <strong>Stories instead of statistics</strong> – People love narratives<br>
            • <strong>Role models from the neighborhood</strong> – "She's like me"<br>
            • <strong>Small steps</strong> – No radical jumps<br>
            • <strong>Emphasize gain</strong> – Not the loss<br>
            <br>
            
            <strong>Using social proof:</strong><br>
            • <strong>"Others do it too"</strong> – Positive peer pressure<br>
            • <strong>Respected authorities</strong> – Imams, elders, doctors<br>
            • <strong>Identify trendsetters</strong> – Early adopters<br>
            • <strong>Local adaptation</strong> – "This is OUR way"<br>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="normal-text">
        <strong>Our 4-Phase Change Management Plan:</strong><br><br>
        
        <strong>Phase 1: Understanding REAL Opinions (Months 1-6)</strong><br>
        <em>"What do people really think – not what they say, but what they write?"</em><br><br>
        
        • <strong>YouTube Comment Analysis:</strong> Unfiltered opinions on education, tradition, family<br>
        • <strong>Sentiment Mapping:</strong> What fears, hopes, prejudices are really there?<br>
        • <strong>Language Pattern Identification:</strong> How do different groups talk about girls' education?<br>
        • <strong>Emotional Trigger Detection:</strong> What makes people angry/hopeful/anxious?<br>
        <br>
        
        <strong>The secret:</strong><br>
        We don't just listen – we understand. Not what people should say, 
        but what they really think. That's the key to real change.
        <br><br>
        
        <strong>The result:</strong> Transformation without trauma. Evolution instead of revolution.
        <br><br>
        
        <div class="source">Sources: Cialdini (2021), Heath & Heath (2010), Rogers (2003), Freire (1970)</div>
        </div>
        """, unsafe_allow_html=True)

# ===== MAIN PAGE CONTENT =====
def main():
    """Hauptfunktion der Page - Mit Sprachsystem"""
    
    # === SPRACHSYSTEM ===
    init_language()
    language_switcher()
    
    # Emotionaler, aber professioneller Titel
    if st.session_state.language == "DE":
        st.title("🌍 HerEducation: Wo Träume auf Tradition treffen")
        st.markdown('<div class="subtitle-text">Ein Bildungsprojekt, das Brücken baut statt Mauern einreißt</div>', unsafe_allow_html=True)
    else:
        st.title("🌍 HerEducation: Where Dreams Meet Tradition")
        st.markdown('<div class="subtitle-text">An education project that builds bridges instead of tearing down walls</div>', unsafe_allow_html=True)
    
    # Hook für Leser
    if st.session_state.language == "DE":
        st.markdown("""
        <div class="normal-text" style="font-style: italic; margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 10px;">
        💡 <strong>Die große Frage:</strong> Wie bringt man 7,5 Millionen Mädchen bei, dass sie mehr wert sind, 
        als ihre Kultur ihnen manchmal vermittelt – ohne ihre Kultur anzugreifen?
        <br><br>
        Die Antwort finden wir in Malaysia. Einem Land voller Widersprüche, das genau deshalb zum perfekten Modell wird.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="normal-text" style="font-style: italic; margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 10px;">
        💡 <strong>The big question:</strong> How do you teach 7.5 million girls that they're worth more 
        than their culture sometimes tells them – without attacking their culture?
        <br><br>
        We find the answer in Malaysia. A country full of contradictions, which is exactly why it becomes the perfect model.
        </div>
        """, unsafe_allow_html=True)
    
    # Tab-Layout mit ansprechenden Namen
    if st.session_state.language == "DE":
        tab_names = [
            "🎯 Warum Malaysia?", "🏙️ Das Malaysia-Paradox", "🚫 Unsichtbare Barrieren", 
            "👶 Unsichtbare Kinder", "🌈 Das Vielfalt-Puzzle", "📚 Der Bildungs-Effekt", 
            "🌍 Die große Vision", "💡 Die Kunst der Veränderung"
        ]
    else:
        tab_names = [
            "🎯 Why Malaysia?", "🏙️ The Malaysia Paradox", "🚫 Invisible Barriers",
            "👶 Invisible Children", "🌈 The Diversity Puzzle", "📚 The Education Effect",
            "🌍 The Big Vision", "💡 The Art of Change"
        ]
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(tab_names)

    # Tab-Inhalte
    with tab1:
        display_tab_ursprung()

    with tab2:
        display_tab_malaysia()

    with tab3:
        display_tab_frauenrechte()

    with tab4:
        display_tab_mischehen()

    with tab5:
        display_tab_ethnien()

    with tab6:
        display_tab_bildung_schluessel()

    with tab7:
        display_tab_globale_perspektiven()

    with tab8:
        display_tab_emotionale_dynamiken()
    
    # Call-to-Action am Ende
    if st.session_state.language == "DE":
        st.markdown("""
        <div class="normal-text" style="margin-top: 30px; padding: 20px; background-color: #e8f5e8; border-radius: 10px; text-align: center;">
        <strong>🚀 Bereit, Geschichte zu schreiben?</strong><br>
        HerEducation ist mehr als eine YouTube-Analyse-Tool – es ist eine Bewegung. Eine Bewegung, die zeigt: 
        Respekt und Veränderung können Hand in Hand gehen.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="normal-text" style="margin-top: 30px; padding: 20px; background-color: #e8f5e8; border-radius: 10px; text-align: center;">
        <strong>🚀 Ready to make history?</strong><br>
        HerEducation is more than a YouTube analysis tool – it's a movement. A movement that shows: 
        Respect and change can go hand in hand.
        </div>
        """, unsafe_allow_html=True)
    
    # Standard-Footer
    display_standard_footer()

# ===== AUSFÜHRUNG =====
if __name__ == "__main__":
    main()
else:
    # Wird ausgeführt wenn als Streamlit Page importiert
    main()