# VLE_Diagrams
This is a Python application used to create Txy and Pxy diagrams for binary mixtures. Uses the Antoine equation for calculations, parameters are scrapped from the NIST Chemistry WebBook. It uses BeautifulSoup for web scrapping and tkinter to GUI development.

User Inputs:
- Compound names
- Pressure
- Temperature

Dropdowns and Checkboxes:
- Units
- Choice to use Raoult's Law in calculations or something else (nonideal, Henry's Law, or Fugacity/Gibbs and the like)
- Choice of which compound to plot by composition
- Choice to ignore the temperature ranges for the Antoine equation parameters in calculation
- Isobaric or Isothermal (Txy or Pxy)
