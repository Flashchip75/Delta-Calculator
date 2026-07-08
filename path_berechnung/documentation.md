# Dokumentation der Trajektorienplanung im Modul Projektarbeit

## Entwicklung einer modularen Trajektorie zur ruckbegrenzten und dynamischen Berechnung eines Delta Roboters

---

## Inhaltsverzeichnis

1. [Einleitung und Problemstellung](#1-einleitung-und-problemstellung)
2. [Mathematische Grundlagen der Bahnplanung](#2-mathematische-grundlagen-der-bahnplanung)
   * [Geometrische Primitiven und Parametrisierung](#geometrische-primitiven-und-parametrisierung)
   * [Differentialgeometrie nach Frenet-Serret](#differentialgeometrie-nach-frenet-serret)
   * [Dynamik u. Zeitgesetze](#dynamik-u-zeitgesetze)
3. [Kinetostatische und Dynamische Kraftanalyse](#3-kinetostatische-und-dynamische-kraftanalyse)
   * [Vektorielle Kraftprojektion](#vektorielle-kraftprojektion)
4. [Datenfluss und Schnittstellendefinition](#4-datenfluss-und-schnittstellendefinition)
5. [Zentrale Konfiguration und Schnittstellenintegration](#5-zentrale-konfiguration-und-schnittstellenintegration)
   * [Typisiertes Konfigurationsmanagement (config.py)](#typisiertes-konfigurationsmanagement-configpy)
   * [Dynamikberechnung und GUI-Schnittstelle (exePath)](#dynamikberechnung-und-gui-schnittstelle-exepath)
6. [Validierung und Ergebnisse](#6-validierung-und-ergebnisse)
7. [Zusammenfassung und Ausblick](#7-zusammenfassung-und-ausblick)

---

## 1. Einleitung und Problemstellung

Die Kernaufgabe bei der Automatisierung eines Delta-Roboters ist die präzise Steuerung seiner Bewegung im dreidimensionalen Raum. Die vorliegende Arbeit befasst sich mit der Trajektorienplanung und deren informationstechnischer Umsetzung.

Die zentrale Herausforderung der Bahnplanung besteht darin, den Weg des Endeffektors von einem definierten Startpunkt zu einem Zielpunkt analytisch zu beschreiben. Anstatt den Roboter sprunghaft zwischen Koordinaten wechseln zu lassen, muss eine kontinuierliche Bahnkurve (Trajektorie) erzeugt werden. Dies geschieht durch die Generierung zeitlich und räumlich diskreter Zwischenpunkte.

Um diese räumlichen Wegpunkte für die Maschinensteuerung nutzbar zu machen, müssen sie in konkrete Stellbefehle übersetzt werden. Hierfür wird die Inverse Kinematik angewendet, welche die kartesischen Koordinaten in die exakten Gelenkwinkel der drei Antriebsachsen transformiert. Gleichzeitig erfordert eine vollständige Auslegung die Berücksichtigung physikalischer Rahmenbedingungen wie das Eigengewicht der Bauteile, Massenträgheiten und maximale Beschleunigungswerte. Nur unter Einbezug dieser Dynamik lassen sich die benötigten Antriebsmotoren korrekt dimensionieren und mechanische Überlastungen während der Bewegung vermeiden.

Ziel dieser Ausarbeitung ist es, diesen Planungs- und Steuerungsprozess systematisch abzubilden. Dafür wird die Entwicklung einer objektorientierten Softwarearchitektur dokumentiert, die den Ablauf von der abstrakten Geometrieeingabe über die Berechnung der Trajektorie bis hin zur automatisierten Motorauswahl nachvollziehbar löst.

---

## 2. Mathematische Grundlagen der Bahnplanung

Die mathematische Beschreibung einer Trajektorie erfordert die Verknüpfung von Raumgeometrie und Zeitverhalten. Eine vollständige Beschreibung des TCP-Zustands zu jedem Zeitpunkt $t$ wird formal über die Abbildung

$$\vec{r}(t) = \begin{pmatrix} x(t) \\ y(t) \\ z(t) \end{pmatrix}$$

realisiert. Zur Beherrschung komplexer Bahnen wird diese Abbildung in eine rein geometrische Beschreibung $\vec{r}(s)$ in Abhängigkeit von der Bogenlänge $s$ und ein zeitabhängiges Wegprofil $s(t)$ zerlegt.

### Geometrische Primitiven und Parametrisierung

Die Raumkurve setzt sich aus einzelnen Segmenten zusammen. Jedes Segment wird über einen internen Parameter $\tau \in [0, 1]$ normiert abgetastet.  
Für lineare Segmente (`Line`) gilt die klassische lineare Interpolation zwischen Startpunkt $\vec{P}_0$ und Zielpunkt $\vec{P}_1$:

$$\vec{P}(\tau) = \vec{P}_0 \cdot (1 - \tau) + \vec{P}_1 \cdot \tau$$

Um weiche Richtungsänderungen im Raum zu ermöglichen, implementiert das System kubische Bézier-Kurven, welche über vier Kontrollpunkte $\vec{P}_0$ bis $\vec{P}_3$ definiert sind:

$$\vec{P}(\tau) = (1-\tau)^3 \vec{P}_0 + 3\tau(1-\tau)^2 \vec{P}_1 + 3\tau^2(1-\tau) \vec{P}_2 + \tau^3 \vec{P}_3$$

Die Ableitungen nach dem Parameter $\tau$ liefern hierbei die Tangentenrichtungen an den Segmentgrenzen, was für das Aneinanderreihen von Kurvenzügen (Erreichung von $G^1$- oder $C^1$-Kontinuität) von zentraler Bedeutung ist.

Die obige Abbildung zeigt die im Code implementierten Elemente bzw. Segmente, aus denen sich der Pfad zusammensetzen kann.

Die Generierung der Punktewolke erfolgt über die einzelnen Segmente, die mit Punkten versehen werden. Für jeden Punkt dieser Wolke wird im späteren Verlauf die Position, Geschwindigkeit, Beschleunigung, der Ruck und die jeweilige Kraft berechnet.

### Differentialgeometrie nach Frenet-Serret

Um physikalische Effekte wie die Zentripetalkraft in Kurven analysieren zu können, muss die Orientierung des Pfades im Raum mathematisch erfasst werden. Dies geschieht über die Frenet-Serret-Formeln. Das begleitende Dreibein besteht aus drei orthogonalen Einheitsvektoren: dem Tangentenvektor $\vec{T}$, dem Hauptnormalenvektor $\vec{N}$ und dem Binormalenvektor $\vec{B}$.

Da die Punkte aus diskreten Trajektorienwolken vorliegen, müssen die Ableitungen numerisch bezüglich der tatsächlichen, akkumulierten Bogenlänge $s$ bestimmt werden. Die erste Ableitung des Ortsvektors nach der Bogenlänge liefert direkt den Tangentialeinheitsvektor:

$$\vec{T}(s) = \frac{d\vec{r}}{ds} \Big/ \left\| \frac{d\vec{r}}{ds} \right\|$$

Die Krümmung $\kappa(s)$ der Kurve beschreibt, wie stark der Pfad von einer Geraden abweicht, und berechnet sich über das Kreuzprodukt der ersten und zweiten Ableitung des Ortes:

$$\kappa(s) = \frac{\left\| \frac{d\vec{r}}{ds} \times \frac{d^2\vec{r}}{ds^2} \right\|}{\left\| \frac{d\vec{r}}{ds} \right\|^3}$$

Der Binormalenvektor steht senkrecht auf der durch $\vec{T}$ und der Beschleunigung aufgespannten Schmiegungsebene:

$$\vec{B}(s) = \frac{\frac{d\vec{r}}{ds} \times \frac{d^2\vec{r}}{ds^2}}{\left\| \frac{d\vec{r}}{ds} \times \frac{d^2\vec{r}}{ds^2} \right\|}$$

Daraus ergibt sich der Hauptnormalenvektor, welcher stets zum lokalen Krümmungsmittelpunkt zeigt, über das orthogonale Komplement:

$$\vec{N}(s) = \vec{B}(s) \times \vec{T}(s)$$

Eine ingenieurtechnische Herausforderung stellt die rechnerische Singularität auf idealen Geraden dar. Ist $\kappa = 0$, bricht die mathematische Definition von $\vec{N}$ und $\vec{B}$ zusammen, da der Betrag des Kreuzproduktes im Nenner gegen Null geht. Numerisch führt dies zu massivem Differentiationsrauschen ("Zittern" der Vektoren). Das System löst dies durch eine harte Toleranzgrenze: Unterschreitet die lokale Krümmung den Wert $\kappa < 10^{-6}$, werden die betroffenen Komponenten explizit auf Null gesetzt, um eine stabile Kraftberechnung zu garantieren.

### Dynamik u. Zeitgesetze

Um den zeitlichen Verlauf auf dem Pfad festzulegen, wurde zu Anfang des Projektes auf ein starres Polynom 5. Grades zurückgegriffen:

$$s(t) = c_0 + c_1 t + c_2 t^2 + c_3 t^3 + c_4 t^4 + c_5 t^5$$

Dieses Profil erlaubt die Definition von sechs Randbedingungen, wodurch Position, Geschwindigkeit und Beschleunigung am Anfang und Ende des Segments gesetzt werden können:

$$\dot{s}(t) = v(t) = c_1 + 2c_2 t + 3c_3 t^2 + 4c_4 t^3 + 5c_5 t^4$$

$$\ddot{s}(t) = a(t) = 2c_2 + 6c_3 t + 12c_4 t^2 + 20c_5 t^3$$

Im Verlauf des Projekts kam die Idee auf, beliebig zu definierende Bewegungsgesetze einzuführen. Dies konnte mit einer neuen Funktion umgesetzt werden. Das Ziel ist, mehrere Segmente hintereinander mit unterschiedlichen Bewegungsgesetzen abzufahren. Beispielsweise eine Beschleunigung auf eine gewisse Geschwindigkeit mit einem Polynom 5. Grades, dann eine konstante Fahrt und anschließend ein Abbremsen mit einem Polynom 7. Grades.

Umgesetzt wird dies durch ein vollständig neues Konzept. Hierbei wirkt der `DeltaUniversalPlaner` als Hauptklasse, die Klassen `TrajectoryMath` und `GeometryEngine` arbeiten dieser zu.

#### TrajectoryMath Klasse

Über die Bedingungen, welche der Benutzer vorgibt, werden in der ersten Funktion die beliebigen Koeffizienten abhängig von der Anzahl der Bedingungen definiert. Mit Hilfe einer Gleichung basierend auf der Fakultät wird eine beliebig große Koeffizientenmatrix zusammengebaut. Im `return` wird diese Matrix gelöst und die Koeffizienten berechnet. Die folgende Funktion berechnet aus den Koeffizienten, der Zeit und dem Parameter `k` den gewünschten Wert. Hierbei steht `k` für die Ordnung der Ableitung.

#### GeometryEngine Klasse

Die Klasse dient als Berechnungsfunktionalität für die Gesamtlänge des Pfades. Diese Daten werden in der Hauptklasse benötigt. Hierfür wird die dreidimensionale Punktewolke eingelesen, woraus die Distanzen zwischen einzelnen Punkten errechnet und aufsummiert werden.

#### DeltaUniversalPlaner

Aus den Daten des letzten Zustands des Vorsegmentes werden Anfangsbedingungen geladen. In einer Fallunterscheidung werden diese Daten entweder genutzt oder verworfen und überschrieben. Ist der Typ des nächsten Zeitgesetzes "konstant", so wird aus dem gewünschten Weg und der vorherigen konstanten Geschwindigkeit eine Dauer des Segments berechnet. Würde man in einer konstanten Fahrt Geschwindigkeit, Zeit und Weg vorgeben, wäre das Segment überdefiniert und führt zu Problemen. Aus diesem Grund wird die Dauer des Segmentes berechnet. Aus diesen Überlegungen entstand demnach die Idee, einen *Presolve* einzuführen, um dem Benutzer eine grobe Zeit des Bewegungsablaufs berechnen zu können. Aus diesen Berechnungen werden für die konstante Fahrt die Bedingungen in `bed` festgehalten.

Abbildung 7 beschreibt die andere Eventualität der Fallunterscheidung. Hierbei werden die Anfangsbedingungen geerbt und die zusätzlich vorhandenen Zielbedingungen angehängt. Am Ende resultiert für beide Fälle ein Vektor aus Bedingungen.

Anschließend werden zu diesem Vektor mit den Funktionen der Klasse `TrajectoryMath` die Koeffizienten berechnet. Für die nachfolgenden Segmente werden zudem mit der Dauer, also dem Endzeitpunkt, die Werte der Geschwindigkeit, Beschleunigung, Position und Ruck berechnet. Darauf basiert die Vererbung für das Folgesegment.

Die Funktion `get_Zustand` basiert auf der bereits erwähnten Funktion in `TrajectoryMath` und berechnet die von Interesse bestehenden Variablen. Die Funktion `finde_zeit_zu_s` führt die Berechnung des inversen Zeitgesetzes mit der numerischen Funktion `brentq` durch und liefert zu jedem Wegpunkt des Pfades eine Zeit $t$.

Der letzte Ausschnitt berechnet auf Basis von `GeometryEngine` die kumulierte Pfadlänge, in welcher zudem der Abstand zwischen jedem Punkt gespeichert ist. Die Funktion wird genutzt, um für jeden dieser Wegpunkte einen Zeitpunkt $t$ zu berechnen. Abschließend werden die Parameter der Dynamik für jeden dieser Zeitpunkte errechnet. Am Ende stehen Ergebnisse, welche zu jedem Wegpunkt den Zeitpunkt, die Geschwindigkeit, Beschleunigung sowie den Ruck enthalten.

---

## 3. Kinetostatische und Dynamische Kraftanalyse

Die am Endeffektor wirkenden Kräfte werden im `DynamicsManager` berechnet. Aus steuerungstechnischer Sicht handelt es sich um eine inverse Dynamik: Aus dem bekannten kinematischen Zustand ($v, a, j$) und den Kurveneigenschaften ($\vec{T}, \vec{N}, \kappa$) wird die erforderliche Antriebskraft berechnet, die der TCP-Aktor aufbringen muss.

### Vektorielle Kraftprojektion

Die translatorische Bewegungsgleichung des TCP lautet unter Berücksichtigung der Schwerkraft nach dem Newtonschen Grundgesetz:

$$\vec{F}_{Aktor} = m \cdot \vec{a}_{TCP} - \vec{F}_g$$

wobei $\vec{F}_g = \begin{pmatrix} 0 & 0 & -m \cdot g \end{pmatrix}^T$. Der Clou der Frenet-Formulierung liegt in der Zerlegung des Beschleunigungsvektors $\vec{a}_{TCP}$ in das bahnbezogene Koordinatensystem. Der Beschleunigungsvektor setzt sich zusammen aus der Tangentialbeschleunigung (Geschwindigkeitsänderung auf der Bahn) und der Zentripetalbeschleunigung (Richtungsänderung im Raum):

$$\vec{a}_{TCP}(t) = \dot{v}(t) \cdot \vec{T}(s) + v^2(t) \cdot \kappa(s) \cdot \vec{N}(s)$$

Daraus resultieren die im Code getrennt ausgewerteten Kraftkomponenten:

$$\vec{F}_t = m \cdot \dot{v} \cdot \vec{T}$$

$$\vec{F}_n = m \cdot v^2 \cdot \kappa \cdot \vec{N}$$

Die Gesamtkraft ergibt sich durch vektorielle Aufsummierung im kartesischen Raum. Diese Vorsteuerung ermöglicht es, die Motormomente vorausschauend anzupassen (*Feed-Forward Control*), noch bevor Schleppfehler durch die Regeldynamik entstehen.

---

## 4. Datenfluss und Schnittstellendefinition

Der Datenfluss der Trajektorienplanung ist modular aufgebaut. Ziel der Schnittstelle ist es, die Eingaben der Benutzeroberfläche in ein Format zu überführen, das von den bestehenden Berechnungsfunktionen weiterverarbeitet werden kann. Dabei werden Geometrie und Zeitverhalten bewusst getrennt behandelt.

Die Benutzeroberfläche liefert zwei Listen zurück:

$$\texttt{ui\_data} = (\texttt{pfade}, \texttt{zeitgesetze})$$

Die Liste `pfade` enthält die geometrischen Segmente, beispielsweise `Line`, `Arc`, `Bezier` oder `Wait`. Die Liste `zeitgesetze` enthält die zugehörigen Bewegungsgesetze, beispielsweise ein Polynom 5. Grades, ein Polynom 7. Grades oder eine Konstantfahrt.

Die Zuordnung zwischen Geometrie und Zeitgesetz erfolgt über die Variable `time_law_ref`. Direkt aufeinanderfolgende Geometrien mit gleicher `time_law_ref` werden zu einem gemeinsamen Pfadabschnitt zusammengefasst. Erst aus diesem gesamten Pfadabschnitt wird anschließend eine Punktewolke erzeugt. Dadurch wirkt ein Zeitgesetz nicht nur auf ein einzelnes geometrisches Segment, sondern auf den gesamten zusammenhängenden Pfadabschnitt.

Der `Jsonconverter` dient als Adapter zwischen dem neuen UI-Format und den bereits vorhandenen Berechnungsfunktionen. Er berechnet selbst keine Punktewolken, sondern wandelt die UI-Daten lediglich in das bisher verwendete interne Kurvenformat um und gruppiert die Segmente anhand der `time_law_ref`. Die eigentliche Punktewolke wird anschließend durch die bestehenden Geometriefunktionen erzeugt.

Der Sonderfall `Wait` wird als eigenes Segment behandelt. Dabei handelt es sich nicht um eine echte Geometrie, sondern um einen Haltebefehl im Bewegungsablauf. Während dieser Zeit bleibt der TCP an der aktuellen Position stehen. Deshalb besitzt `Wait` kein normales Zeitgesetz und wird nicht mit benachbarten Bewegungssegmenten zusammengefasst.

### Zusammenfassung des Datenflusses

1. Die Benutzeroberfläche erzeugt Geometrien und Zeitgesetze.
2. Der `Jsonconverter` gruppiert aufeinanderfolgende Geometrien mit gleicher `time_law_ref`.
3. Die gruppierten Geometrien werden in das bisherige interne Kurvenformat überführt.
4. Aus jeder Kurvengruppe wird eine gemeinsame Punktewolke berechnet.
5. Der `DeltaUniversalPlaner` verknüpft jede Punktewolke mit dem zugehörigen Zeitgesetz.
6. Anschließend werden Geschwindigkeit, Beschleunigung, Ruck und die dynamischen Größen berechnet.

Durch diese Struktur bleibt die Schnittstelle flexibel. Neue Geometrien oder zusätzliche Zeitgesetze können ergänzt werden, ohne dass die gesamte Berechnungskette angepasst werden muss. Gleichzeitig können die bereits bestehenden Funktionen zur Punktewolkenberechnung und Dynamikplanung weiterverwendet werden.

---

## 5. Zentrale Konfiguration und Schnittstellenintegration

Um einen reibungslosen Ablauf und Datenaustausch zwischen den verschiedenen Projektgruppen zu gewährleisten, wurde eine modulare Softwarearchitektur implementiert. Eine zentrale Rolle spielen dabei das Konfigurationsmanagement sowie das Hauptintegrationsmodul der Pfadberechnung.

### Typisiertes Konfigurationsmanagement (`config.py`)

Dieses Modul fungiert als zentrale *Single-Source-of-Truth* für sämtliche statischen Pipeline-Parameter. Durch das einmalige Einlesen einer `config.json` und die Kapselung der Werte in strukturierte, typisierte `dataclasses` (u.a. `GlobalConfig`, `WorkspaceConfig`, `PathConfig`) wird eine typsichere Datenbasis geschaffen. Dies verhindert den fehleranfälligen Gebrauch sogenannter *Magic Numbers* im Code und stellt sicher, dass alle Gruppen global konsistent auf Arbeitsraumgrenzen, Motorparameter und globale Systemvariablen zugreifen können.

### Dynamikberechnung und GUI-Schnittstelle (`exePath`)

Die Klasse `exePath` kapselt die Hauptlogik der Trajektoriengenerierung und bildet die primäre Schnittstelle zur GUI-Gruppe. Die Kernmethode `run()` zeichnet sich durch eine flexible, priorisierte Eingabeverarbeitung aus:

* **Geometrieprofile (JSON):** Direkte Übergabe vordefinierter Profile, primär genutzt für systematisches Debugging.
* **G-Code:** Parsing und Konvertierung standardisierter CNC-Befehle in berechenbare Pfadsegmente.
* **UI-Daten:** Reguläre Datenübergabe aus der grafischen Oberfläche (Tupel aus Geometrien und Zeitgesetzen), welche über den `UIProfileConverter` in das interne Solver-Format übersetzt werden.

Nach der Extraktion der Punktewolken werden sämtliche mathematischen Operationen, wie die komplexe Dynamik- und Kinematikberechnung der Arbeitsgruppe, zentral aufgerufen und auf die Pfaddaten angewendet.

Der primäre Fokus dieser Integrationsschicht liegt jedoch auf der präventiven Fehlerbehandlung (*Exception Handling*). Um Rechenzeit zu sparen und fehlerhafte Zustände im mathematischen Solver zu vermeiden, werden alle Eingangsdaten vor der Verarbeitung strikt validiert. So prüft der Code detailliert die Integrität der GUI-Daten (z. B. ob es sich um korrekte Tupel aus nicht-leeren Listen für Geometrien und Zeitgesetze handelt) und validiert Dateiendungen beim Einlesen von G-Code. Werden Inkonsistenzen oder fehlende Pfade erkannt, wirft das System sofort präzise `ValueErrors`. Zusätzlich ist eine Validierungsfunktion implementiert (`validate_path_continuity`), die aufeinanderfolgende Segmente auf physische Lücken prüft und den Prozess bei Diskontinuitäten mit exakten Koordinatenangaben abbricht.

Erst wenn die Fehlerfreiheit der Eingangsdaten sichergestellt ist und die Berechnungen erfolgreich durchlaufen wurden, werden die resultierenden Trajektoriendaten als strukturiertes Dictionary zurückgegeben und parallel zur lückenlosen Dokumentation als CSV-Datei exportiert.

---

## 6. Validierung und Ergebnisse

Nach erfolgreichem Durchlauf der Berechnungspipeline ruft `Mastermain.py` das Visualisierungsmodul `Plotter` auf. Dieses stellt die zeitlichen Verläufe von Weg, Geschwindigkeit, Beschleunigung und Ruck in einem Multiplot-Fenster dar. Parallel dazu wird eine animierte 3D-Darstellung der Raumkurve generiert, in welcher das Frenet-Dreibein sowie die Beträge der Aktorkräfte als Vektorpfeile dynamisch mitgeführt werden.

Dies ist der Stand des eigenständigen Codes der Trajektorie. Die Visualisierung wird im zusammengebauten Projekt nun durch die GUI übernommen.

Diese Validierung erlaubt es dem Projektingenieur, kritische Bahnabschnitte – beispielsweise enge Kurvenradien bei hoher Bahngeschwindigkeit – sofort visuell zu identifizieren. Überhöhte Ausschläge der Normalkraft $\vec{F}_n$ oder Ruckspitzen können so vor dem realen Testbetrieb am physikalischen Roboter optimiert werden, um mechanische Schäden oder Notabschaltungen der Antriebsregler effektiv zu verhindern.

---

## 7. Zusammenfassung und Ausblick

Das realisierte Softwaresystem stellt eine robuste, mathematisch geschlossene und numerisch stabile Lösung zur Trajektorienberechnung dar. Durch die konsequente Nutzung von Polynomen 5. Grades wird die geforderte Ruckbegrenzung lückenlos umgesetzt. Die differentialgeometrische Aufbereitung der Raumkurven ermöglicht eine präzise kinetostatische Vorsteuerung der Antriebskräfte.

Für zukünftige Erweiterungsstufen bietet die modulare Architektur optimale Voraussetzungen. Sinnvolle nächste Schritte sind die Integration eines inversen kinematischen Modells speziell für die Gelenkwinkelkoordinaten des Delta-Roboters sowie die Implementierung einer automatischen Geschwindigkeitsabsenkung in Bereichen maximaler Kurvenkrümmung (*Adaptive Speed Scheduling*).
