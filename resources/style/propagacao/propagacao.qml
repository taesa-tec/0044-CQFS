<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.18.17" minimumScale="inf" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <pipe>
    <rasterrenderer opacity="1" alphaBand="-1" classificationMax="288" classificationMinMaxOrigin="User" band="1" classificationMin="0" type="singlebandpseudocolor">
      <rasterTransparency/>
      <rastershader>
        <colorrampshader colorRampType="DISCRETE" clip="0">
          <item alpha="255" value="49" label="&lt; 50" color="#b50106"/>
          <item alpha="255" value="99" label="&lt; 100" color="#feab03"/>
          <item alpha="255" value="149" label="&lt; 150" color="#fffd0f"/>
          <item alpha="255" value="199" label="&lt; 200" color="#94e509"/>
          <item alpha="255" value="294" label="> 200" color="#00764e"/>
          <item alpha="255" value="295" label="Sem Risco" color="#000000"/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0"/>
    <huesaturation colorizeGreen="128" colorizeOn="0" colorizeRed="255" colorizeBlue="128" grayscaleMode="0" saturation="0" colorizeStrength="100"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
