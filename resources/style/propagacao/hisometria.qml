<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.18.17" minimumScale="inf" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <pipe>
    <rasterrenderer opacity="1" alphaBand="-1" classificationMax="525" classificationMinMaxOrigin="CumulativeCutFullExtentEstimated" band="1" classificationMin="196" type="singlebandpseudocolor">
      <rasterTransparency/>
      <rastershader>
        <colorrampshader colorRampType="DISCRETE" clip="0">
          <item alpha="255" value="200" label="&lt;= 200" color="#d7191c"/>
          <item alpha="255" value="299" label="200 - 299" color="#fdae61"/>
          <item alpha="255" value="499" label="459 - 499" color="#ffffbf"/>
          <item alpha="255" value="inf" label="> 499" color="#2b83ba"/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0"/>
    <huesaturation colorizeGreen="128" colorizeOn="0" colorizeRed="255" colorizeBlue="128" grayscaleMode="0" saturation="0" colorizeStrength="100"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
