# Shaders

# Documentation complète : Créer ses propres shaders sur Source Engine

## 📚 Table des matières

1. [Introduction](#introduction)
2. [Prérequis](#prérequis)
3. [Architecture d'un shader Source](#architecture)
4. [Partie 1 : Le Pixel Shader (HLSL)](#pixel-shader)
5. [Partie 2 : Le Vertex Shader (HLSL)](#vertex-shader)
6. [Partie 3 : Le code C++ (Interface)](#code-cpp)
7. [Compilation et intégration](#compilation)
8. [Paramètres avancés](#parametres-avances)
9. [Exemples pratiques](#exemples)
10. [Debugging et optimisation](#debugging)
11. [Ressources](#ressources)

---

<a name="introduction"></a>
## 🎯 Introduction

### Qu'est-ce qu'un shader ?

Un **shader** est un programme qui s'exécute sur le GPU pour déterminer comment afficher les surfaces 3D. Dans Source Engine, un shader complet se compose de **3 parties** :

```
┌─────────────────────────────────────┐
│   SHADER COMPLET SOURCE ENGINE      │
├─────────────────────────────────────┤
│ 1. Vertex Shader (.fxc)             │ ← Transforme la géométrie
│    └─ HLSL (langage de shader)      │
├─────────────────────────────────────┤
│ 2. Pixel Shader (.fxc)              │ ← Colore les pixels
│    └─ HLSL (langage de shader)      │
├─────────────────────────────────────┤
│ 3. Code C++ (.cpp)                  │ ← Interface avec le moteur
│    └─ Définit les paramètres VMT    │
└─────────────────────────────────────┘
```

### Workflow général

```
1. Écrire le HLSL (.fxc)
   ↓
2. Compiler → .vcs (bytecode)
   ↓
3. Écrire le C++ (.cpp)
   ↓
4. Compiler → stdshader_dx9.dll
   ↓
5. Créer un VMT
   ↓
6. Utiliser dans le jeu !
```

---

<a name="prérequis"></a>
## 🛠️ Prérequis

### Logiciels requis

- **Source SDK 2013** ([GitHub](https://github.com/ValveSoftware/source-sdk-2013))
- **Visual Studio 2013+** (Community Edition gratuite)
- **Perl** ([ActivePerl](https://www.activestate.com/products/perl/))
- **DirectX SDK June 2010** ([Microsoft](https://www.microsoft.com/en-us/download/details.aspx?id=6812))

### Connaissances recommandées

- ✅ Bases de C++ (classes, pointeurs)
- ✅ Bases de HLSL ou GLSL
- ✅ Concepts 3D (vertices, UV, normales)
- ⚠️ Pas besoin d'être expert !

---

<a name="architecture"></a>
## 🏗️ Architecture d'un shader Source

### Les 3 composants essentiels

#### 1. Vertex Shader (VS)
**Rôle** : Transforme chaque sommet 3D
```
INPUT: Position 3D, UV, Normales, etc.
  ↓
TRAITEMENT: Transformations matrices
  ↓
OUTPUT: Position écran, données interpolées
```

#### 2. Pixel Shader (PS)
**Rôle** : Calcule la couleur de chaque pixel
```
INPUT: UV, normales interpolées
  ↓
TRAITEMENT: Textures, éclairage, effets
  ↓
OUTPUT: Couleur finale RGBA
```

#### 3. Code C++ (Interface)
**Rôle** : Connecte HLSL ↔ Moteur
```
- Définit les paramètres VMT
- Charge les textures
- Configure le pipeline
- Gère les versions de shaders
```

---

<a name="pixel-shader"></a>
## 🎨 Partie 1 : Le Pixel Shader (HLSL)

### Structure de base

```hlsl
// myshader_ps20b.fxc
// Pixel Shader pour Source Engine

// ===== SAMPLERS (Textures) =====
sampler BaseTextureSampler : register(s0);
sampler NormalMapSampler   : register(s1);

// ===== CONSTANTES =====
const float4 g_Color : register(c0);

// ===== STRUCTURE D'ENTRÉE =====
struct PS_INPUT
{
    float2 vTexCoord0      : TEXCOORD0;   // Coordonnées UV
    float3 vWorldNormal    : TEXCOORD1;   // Normale (interpolée)
    float3 vWorldPos       : TEXCOORD2;   // Position monde
    float4 vColor          : COLOR0;      // Couleur vertex
};

// ===== FONCTION PRINCIPALE =====
float4 main( PS_INPUT i ) : COLOR
{
    // 1. Échantillonner la texture de base
    float4 baseColor = tex2D( BaseTextureSampler, i.vTexCoord0 );
    
    // 2. Appliquer la couleur du vertex
    baseColor *= i.vColor;
    
    // 3. Retourner la couleur finale
    return baseColor;
}
```

### Éléments importants

#### Samplers (Textures)
```hlsl
sampler MyTextureSampler : register(s0);
//      ↑                           ↑
//      Nom                    Slot de texture (s0-s15)
```

**Slots disponibles** :
- `s0` à `s15` = 16 textures maximum

#### Constantes (Paramètres)
```hlsl
const float4 g_MyParam : register(c0);
//            ↑                    ↑
//            Nom               Registre constant
```

**Types disponibles** :
- `float` = Nombre décimal
- `float2` = Vecteur 2D (x, y)
- `float3` = Vecteur 3D (x, y, z)
- `float4` = Vecteur 4D (x, y, z, w) ou couleur RGBA

#### Fonctions utiles

```hlsl
// Échantillonner une texture
float4 color = tex2D( sampler, uv );

// Normaliser un vecteur
float3 normal = normalize( vNormal );

// Produit scalaire (dot product)
float ndotl = dot( normal, lightDir );

// Clamp (limiter entre 0 et 1)
float value = saturate( ndotl );

// Mélanger deux couleurs
float4 result = lerp( colorA, colorB, factor );
```

### Exemple : Shader avec éclairage simple

```hlsl
// myshader_ps20b.fxc
sampler BaseTextureSampler : register(s0);

const float3 g_LightDir : register(c0);    // Direction lumière
const float4 g_LightColor : register(c1);  // Couleur lumière

struct PS_INPUT
{
    float2 vTexCoord0   : TEXCOORD0;
    float3 vWorldNormal : TEXCOORD1;
};

float4 main( PS_INPUT i ) : COLOR
{
    // Texture de base
    float4 baseColor = tex2D( BaseTextureSampler, i.vTexCoord0 );
    
    // Normaliser la normale
    float3 normal = normalize( i.vWorldNormal );
    
    // Calculer l'éclairage (Lambert)
    float ndotl = saturate( dot( normal, g_LightDir ) );
    
    // Couleur finale = texture × lumière
    float4 finalColor = baseColor * g_LightColor * ndotl;
    
    // Ajouter une lumière ambiante minimale
    finalColor.rgb += baseColor.rgb * 0.2;
    
    return finalColor;
}
```

---

<a name="vertex-shader"></a>
## 🔺 Partie 2 : Le Vertex Shader (HLSL)

### Structure de base

```hlsl
// myshader_vs20.fxc
// Vertex Shader pour Source Engine

// ===== CONSTANTES (Matrices) =====
const float4x4 cModelViewProj : register(c0);  // Matrice MVP combinée

// ===== STRUCTURE D'ENTRÉE =====
struct VS_INPUT
{
    float3 vPos        : POSITION;    // Position 3D
    float3 vNormal     : NORMAL;      // Normale
    float2 vTexCoord0  : TEXCOORD0;   // UV
    float4 vColor      : COLOR0;      // Couleur vertex
};

// ===== STRUCTURE DE SORTIE =====
struct VS_OUTPUT
{
    float4 vPosition   : POSITION;    // Position écran (obligatoire)
    float2 vTexCoord0  : TEXCOORD0;   // UV (vers pixel shader)
    float4 vColor      : COLOR0;      // Couleur (vers pixel shader)
};

// ===== FONCTION PRINCIPALE =====
VS_OUTPUT main( const VS_INPUT v )
{
    VS_OUTPUT o;
    
    // 1. Transformer la position en espace écran
    o.vPosition = mul( float4( v.vPos, 1.0f ), cModelViewProj );
    
    // 2. Passer les coordonnées UV
    o.vTexCoord0 = v.vTexCoord0;
    
    // 3. Passer la couleur
    o.vColor = v.vColor;
    
    return o;
}
```

### Transformations importantes

#### Matrice Model-View-Projection (MVP)
```hlsl
// Transforme position objet → position écran
float4 screenPos = mul( float4( worldPos, 1.0 ), cModelViewProj );
```

#### Transformation de normales
```hlsl
// Les normales doivent être transformées différemment
float3 worldNormal = mul( v.vNormal, (float3x3)cModel );
worldNormal = normalize( worldNormal );
```

### Exemple : Vertex Shader avec animation

```hlsl
// wave_vs20.fxc
const float4x4 cModelViewProj : register(c0);
const float g_Time : register(c20);  // Temps du jeu

struct VS_INPUT
{
    float3 vPos       : POSITION;
    float2 vTexCoord0 : TEXCOORD0;
};

struct VS_OUTPUT
{
    float4 vPosition  : POSITION;
    float2 vTexCoord0 : TEXCOORD0;
};

VS_OUTPUT main( const VS_INPUT v )
{
    VS_OUTPUT o;
    
    // Position modifiée
    float3 pos = v.vPos;
    
    // Animation de vague
    float wave = sin( v.vPos.x * 2.0 + g_Time ) * 0.1;
    pos.z += wave;
    
    // Transformation finale
    o.vPosition = mul( float4( pos, 1.0 ), cModelViewProj );
    o.vTexCoord0 = v.vTexCoord0;
    
    return o;
}
```

---

<a name="code-cpp"></a>
## 💻 Partie 3 : Le code C++ (Interface)

### Structure complète d'un shader

```cpp
// myshader.cpp
#include "BaseVSShader.h"
#include "tier0/memdbgon.h"

// ===== DÉCLARATION DU SHADER =====
BEGIN_VS_SHADER( MyShader, "Help text for MyShader" )
    
    // ===== PARAMÈTRES VMT =====
    BEGIN_SHADER_PARAMS
        SHADER_PARAM( BASETEXTURE, SHADER_PARAM_TYPE_TEXTURE, "shadertest/BaseTexture", "Base texture" )
        SHADER_PARAM( NORMALMAP, SHADER_PARAM_TYPE_TEXTURE, "", "Normal map" )
        SHADER_PARAM( TINTCOLOR, SHADER_PARAM_TYPE_COLOR, "[1 1 1]", "Tint color" )
        SHADER_PARAM( INTENSITY, SHADER_PARAM_TYPE_FLOAT, "1.0", "Effect intensity" )
    END_SHADER_PARAMS

    // ===== INITIALISATION DES PARAMÈTRES =====
    SHADER_INIT_PARAMS()
    {
        // Valeurs par défaut si non définies
        if ( !params[BASETEXTURE]->IsDefined() )
        {
            params[BASETEXTURE]->SetStringValue( "shadertest/BaseTexture" );
        }
        
        if ( !params[TINTCOLOR]->IsDefined() )
        {
            params[TINTCOLOR]->SetVecValue( 1.0f, 1.0f, 1.0f );
        }
    }

    // ===== SHADER DE FALLBACK =====
    SHADER_FALLBACK
    {
        // Si le GPU ne supporte pas SM 2.0
        if ( g_pHardwareConfig->GetDXSupportLevel() < 90 )
        {
            return "UnlitGeneric";
        }
        return 0;
    }

    // ===== INITIALISATION =====
    SHADER_INIT
    {
        // Charger les textures
        if ( params[BASETEXTURE]->IsDefined() )
        {
            LoadTexture( BASETEXTURE );
        }
        
        if ( params[NORMALMAP]->IsDefined() )
        {
            LoadTexture( NORMALMAP );
        }
    }

    // ===== RENDU =====
    SHADER_DRAW
    {
        // ===== ÉTAT STATIQUE (une fois par matériau) =====
        SHADOW_STATE
        {
            // Activer les textures
            pShaderShadow->EnableTexture( SHADER_SAMPLER0, true );  // Base
            pShaderShadow->EnableTexture( SHADER_SAMPLER1, true );  // Normal
            
            // Format du vertex
            int fmt = VERTEX_POSITION | VERTEX_NORMAL | VERTEX_COLOR;
            pShaderShadow->VertexShaderVertexFormat( fmt, 1, 0, 0 );

            // Déclarer les shaders
            DECLARE_STATIC_VERTEX_SHADER( myshader_vs20 );
            SET_STATIC_VERTEX_SHADER( myshader_vs20 );

            if ( g_pHardwareConfig->SupportsPixelShaders_2_b() )
            {
                DECLARE_STATIC_PIXEL_SHADER( myshader_ps20b );
                SET_STATIC_PIXEL_SHADER( myshader_ps20b );
            }
            else
            {
                DECLARE_STATIC_PIXEL_SHADER( myshader_ps20 );
                SET_STATIC_PIXEL_SHADER( myshader_ps20 );
            }
        }
        
        // ===== ÉTAT DYNAMIQUE (chaque frame) =====
        DYNAMIC_STATE
        {
            // Binder les textures
            BindTexture( SHADER_SAMPLER0, BASETEXTURE, FRAME );
            
            if ( params[NORMALMAP]->IsDefined() )
            {
                BindTexture( SHADER_SAMPLER1, NORMALMAP );
            }
            
            // Envoyer des constantes au shader
            float color[4];
            params[TINTCOLOR]->GetVecValue( color, 3 );
            color[3] = params[INTENSITY]->GetFloatValue();
            pShaderAPI->SetPixelShaderConstant( 0, color );

            // Activer les shaders dynamiques
            DECLARE_DYNAMIC_VERTEX_SHADER( myshader_vs20 );
            SET_DYNAMIC_VERTEX_SHADER( myshader_vs20 );

            if ( g_pHardwareConfig->SupportsPixelShaders_2_b() )
            {
                DECLARE_DYNAMIC_PIXEL_SHADER( myshader_ps20b );
                SET_DYNAMIC_PIXEL_SHADER( myshader_ps20b );
            }
            else
            {
                DECLARE_DYNAMIC_PIXEL_SHADER( myshader_ps20 );
                SET_DYNAMIC_PIXEL_SHADER( myshader_ps20 );
            }
        }
        
        // Dessiner
        Draw();
    }

END_SHADER
```

### Types de paramètres VMT

```cpp
// Texture
SHADER_PARAM( NAME, SHADER_PARAM_TYPE_TEXTURE, "path/texture", "Description" )

// Couleur RGB
SHADER_PARAM( NAME, SHADER_PARAM_TYPE_COLOR, "[1 0 0]", "Description" )

// Nombre décimal
SHADER_PARAM( NAME, SHADER_PARAM_TYPE_FLOAT, "1.0", "Description" )

// Nombre entier
SHADER_PARAM( NAME, SHADER_PARAM_TYPE_INTEGER, "0", "Description" )

// Vecteur 2D
SHADER_PARAM( NAME, SHADER_PARAM_TYPE_VEC2, "[0 0]", "Description" )

// Vecteur 3D
SHADER_PARAM( NAME, SHADER_PARAM_TYPE_VEC3, "[0 0 0]", "Description" )

// Vecteur 4D
SHADER_PARAM( NAME, SHADER_PARAM_TYPE_VEC4, "[0 0 0 0]", "Description" )

// Matrice
SHADER_PARAM( NAME, SHADER_PARAM_TYPE_MATRIX, "center .5 .5", "Description" )

// Booléen
SHADER_PARAM( NAME, SHADER_PARAM_TYPE_BOOL, "0", "Description" )
```

### Envoyer des données au shader

```cpp
// Constante float4
float data[4] = { 1.0f, 0.5f, 0.2f, 1.0f };
pShaderAPI->SetPixelShaderConstant( 0, data );  // Registre c0

// Matrice 4×4
float matrix[16];
pShaderAPI->SetVertexShaderConstant( 0, matrix, 4 );  // c0-c3

// Depuis un paramètre VMT
float color[4];
params[TINTCOLOR]->GetVecValue( color, 3 );
pShaderAPI->SetPixelShaderConstant( 1, color );
```

---

<a name="compilation"></a>
## 🔨 Compilation et intégration

### Étape 1 : Compiler les shaders HLSL

#### A. Configurer buildsdkshaders.bat

Éditez `src/materialsystem/stdshaders/buildsdkshaders.bat` :

```batch
set GAMEDIR=D:\SteamLibrary\steamapps\common\Source SDK Base 2013 Multiplayer\granny
set SDKBINDIR=D:\SteamLibrary\steamapps\common\Source SDK Base 2013 Multiplayer\bin
```

#### B. Ajouter vos shaders à la liste

Éditez `stdshader_dx9_20b.txt` et ajoutez :

```
myshader_vs20
myshader_ps20b
```

#### C. Compiler

```batch
cd src\materialsystem\stdshaders
buildsdkshaders.bat
```

**Résultat** : Fichiers `.vcs` générés dans `game/shaders/fxc/`

### Étape 2 : Compiler la DLL C++

#### A. Ouvrir la solution Visual Studio

```
src/materialsystem/stdshaders/stdshader_dx9_20b.sln
```

#### B. Ajouter votre fichier .cpp

1. Clic droit sur **stdshader_dx9** → **Add** → **Existing Item**
2. Sélectionnez `myshader.cpp`

#### C. Compiler

1. **Build** → **Configuration Manager** → **Release**
2. **Build** → **Build Solution** (F7)

**Résultat** : `game/bin/stdshader_dx9.dll`

### Étape 3 : Installer les fichiers

Copiez dans votre mod :

```
game/
├── bin/
│   └── stdshader_dx9.dll        ← DLL compilée
└── shaders/
    └── fxc/
        ├── myshader_vs20.vcs    ← Shaders compilés
        └── myshader_ps20b.vcs
```

### Étape 4 : Créer un VMT

`materials/custom/test.vmt` :

```vmt
"MyShader"
{
    "$basetexture" "custom/test"
    "$normalmap" "custom/test_normal"
    "$tintcolor" "[1 0.5 0.2]"
    "$intensity" "1.5"
}
```

### Étape 5 : Tester

1. Lancez votre jeu
2. Console : `mat_reloadallmaterials`
3. Appliquez le matériau
4. ✅ Votre shader fonctionne !

---

<a name="parametres-avances"></a>
## ⚙️ Paramètres avancés

### Blending et transparence

```cpp
SHADOW_STATE
{
    // Activer la transparence
    pShaderShadow->EnableBlending( true );
    pShaderShadow->BlendFunc( SHADER_BLEND_SRC_ALPHA, SHADER_BLEND_ONE_MINUS_SRC_ALPHA );
    
    // Activer alpha test
    pShaderShadow->EnableAlphaTest( true );
    pShaderShadow->AlphaFunc( SHADER_ALPHAFUNC_GREATER, 0.5f );
}
```

### Culling

```cpp
// Désactiver le culling (afficher les deux faces)
pShaderShadow->EnableCulling( false );

// Culling personnalisé
pShaderShadow->CullMode( SHADER_CULLMODE_CW );  // Clockwise
```

### Depth testing

```cpp
// Désactiver le Z-buffer
pShaderShadow->EnableDepthWrites( false );
pShaderShadow->EnableDepthTest( false );
```

### Combos dynamiques

Pour des variations de shader :

```cpp
BEGIN_SHADER_PARAMS
    SHADER_PARAM( USE_NORMALMAP, SHADER_PARAM_TYPE_BOOL, "0", "Use normal mapping" )
END_SHADER_PARAMS

// Dans SHADER_DRAW
SHADOW_STATE
{
    // Créer des combos basés sur les paramètres
    DECLARE_STATIC_PIXEL_SHADER( myshader_ps20b );
    SET_STATIC_PIXEL_SHADER_COMBO( USE_NORMALMAP, params[USE_NORMALMAP]->GetIntValue() );
    SET_STATIC_PIXEL_SHADER( myshader_ps20b );
}
```

---

<a name="exemples"></a>
## 📖 Exemples pratiques

### Exemple 1 : Shader de brillance (Rim Lighting)

#### Pixel Shader
```hlsl
// rimlight_ps20b.fxc
sampler BaseTextureSampler : register(s0);

const float3 g_CameraPos : register(c0);
const float3 g_RimColor : register(c1);
const float g_RimPower : register(c2);

struct PS_INPUT
{
    float2 vTexCoord0   : TEXCOORD0;
    float3 vWorldPos    : TEXCOORD1;
    float3 vWorldNormal : TEXCOORD2;
};

float4 main( PS_INPUT i ) : COLOR
{
    // Texture de base
    float4 baseColor = tex2D( BaseTextureSampler, i.vTexCoord0 );
    
    // Calculer le rim lighting
    float3 viewDir = normalize( g_CameraPos - i.vWorldPos );
    float3 normal = normalize( i.vWorldNormal );
    
    float rim = 1.0 - saturate( dot( viewDir, normal ) );
    rim = pow( rim, g_RimPower );
    
    // Ajouter la brillance
    float3 rimLight = g_RimColor * rim;
    baseColor.rgb += rimLight;
    
    return baseColor;
}
```

### Exemple 2 : Shader de dissolution

#### Pixel Shader
```hlsl
// dissolve_ps20b.fxc
sampler BaseTextureSampler : register(s0);
sampler NoiseSampler : register(s1);

const float g_DissolveAmount : register(c0);

struct PS_INPUT
{
    float2 vTexCoord0 : TEXCOORD0;
};

float4 main( PS_INPUT i ) : COLOR
{
    float4 baseColor = tex2D( BaseTextureSampler, i.vTexCoord0 );
    float noise = tex2D( NoiseSampler, i.vTexCoord0 ).r;
    
    // Dissolve basé sur le bruit
    float dissolve = step( noise, g_DissolveAmount );
    
    // Bordure brillante
    float edge = smoothstep( g_DissolveAmount - 0.1, g_DissolveAmount, noise );
    baseColor.rgb += edge * float3(1, 0.5, 0);
    
    // Alpha
    baseColor.a *= dissolve;
    
    return baseColor;
}
```

### Exemple 3 : Shader de déformation (Water)

#### Vertex Shader
```hlsl
// water_vs20.fxc
const float4x4 cModelViewProj : register(c0);
const float g_Time : register(c20);
const float g_WaveSpeed : register(c21);
const float g_WaveHeight : register(c22);

struct VS_INPUT
{
    float3 vPos : POSITION;
    float2 vTexCoord0 : TEXCOORD0;
};

struct VS_OUTPUT
{
    float4 vPosition : POSITION;
    float2 vTexCoord0 : TEXCOORD0;
    float2 vTexCoord1 : TEXCOORD1;
};

VS_OUTPUT main( const VS_INPUT v )
{
    VS_OUTPUT o;
    
    float3 pos = v.vPos;
    
    // Deux vagues qui se croisent
    float wave1 = sin( pos.x * 2.0 + g_Time * g_WaveSpeed ) * g_WaveHeight;
    float wave2 = sin( pos.y * 1.5 - g_Time * g_WaveSpeed * 0.7 ) * g_WaveHeight;
    
    pos.z += wave1 + wave2;
    
    o.vPosition = mul( float4( pos, 1.0 ), cModelViewProj );
    
    // UV animées
    o.vTexCoord0 = v.vTexCoord0 + float2( g_Time * 0.05, 0 );
    o.vTexCoord1 = v.vTexCoord0 * 2.0 - float2( 0, g_Time * 0.03 );
    
    return o;
}
```

---

<a name="debugging"></a>
## 🐛 Debugging et optimisation

### Commandes console utiles

```
// Recharger tous les matériaux
mat_reloadallmaterials

// Voir les textures manquantes
mat_showlowresimage 1

// Afficher les shaders utilisés
mat_debug 1

// Wireframe
mat_wireframe 1

// Pas de textures
mat_fullbright 1

// Voir les normales
mat_normals 1

// FPS
cl_showfps 1
```

### Vérifier les erreurs de shader

```cpp
// Ajouter des warnings dans le code
Warning( "MyShader: Parameter not defined\n" );

// Log dans la console
Msg( "MyShader: Value = %f\n", value );
```

### Optimisation

#### 1. Réduire les instructions
```hlsl
// ❌ Lent
float result = pow( value, 2.0 );

// ✅ Rapide
float result = value * value;
```

#### 2. Utiliser des approximations
```hlsl
// ❌ Lent
float result = normalize( vector );

// ✅ Rapide (si déjà presque normalisé)
float result = vector * rsqrt( dot( vector, vector ) );
```

#### 3. Précalculer dans le vertex shader
```hlsl
// Mieux de calculer dans VS et interpoler que de recalculer dans chaque pixel
```

#### 4. Limiter les samplers
```hlsl
// Maximum 16 textures, mais moins = plus rapide
```

### Profiling

```cpp
// Dans le code C++
PIXEvent pixEvent( pShaderAPI, "MyShader Draw" );
// ... code de rendu ...
```

---



# Convention de nommage des shaders Source Engine

## 📝 Format général

```
NomShader_[type][version].[extension]
```

## 🎯 Décryptage de vos exemples

### `BlurFilter_ps11.psh`
- **ps** = Pixel Shader (traite chaque pixel)
- **11** = Shader Model 1.1
- **.psh** = Pixel Shader Header (ancien format)

### `BlurFilter_ps2x.fxc`
- **ps** = Pixel Shader
- **2x** = Shader Model 2.x (peut être 2.0, 2.0a, ou 2.0b)
- **.fxc** = HLSL source file

### `BlurFilter_vs11.fxc`
- **vs** = Vertex Shader (traite chaque vertex/sommet)
- **11** = Shader Model 1.1
- **.fxc** = HLSL source file

### `BlurFilter_vs20.fxc`
- **vs** = Vertex Shader
- **20** = Shader Model 2.0
- **.fxc** = HLSL source file

---

## 🔤 Types de shaders

### **ps** = Pixel Shader
- S'exécute pour **chaque pixel** à l'écran
- Gère : couleurs, textures, éclairage par pixel, effets visuels
- **Exemple** : Appliquer un flou, des reflets, de la brillance

### **vs** = Vertex Shader
- S'exécute pour **chaque sommet** du modèle 3D
- Gère : position, transformation, déformation de la géométrie
- **Exemple** : Animation de vertices, déformation de l'eau

---

## 🔢 Versions des Shader Models

### Shader Model 1.x (SM 1.x)
```
_ps11    → Pixel Shader 1.1
_vs11    → Vertex Shader 1.1
_ps14    → Pixel Shader 1.4
```
- **GPU** : GeForce 3/4, Radeon 8500
- **Limites** : Très basique, peu d'instructions
- **Usage** : Fallback pour vieux GPU

### Shader Model 2.0 (SM 2.0)
```
_ps20    → Pixel Shader 2.0
_vs20    → Vertex Shader 2.0
_ps2x    → Pixel Shader 2.0/2.0a/2.0b (version flexible)
```
- **GPU** : GeForce FX, Radeon 9700+
- **Limites** : 96-512 instructions
- **Usage** : Version standard pour Source Engine

### Shader Model 2.0b (SM 2.0b)
```
_ps20b   → Pixel Shader 2.0b
```
- **GPU** : GeForce 6/7, Radeon X1000+
- **Limites** : 512+ instructions
- **Usage** : Version étendue, plus de fonctionnalités

### Shader Model 3.0 (SM 3.0)
```
_ps30    → Pixel Shader 3.0
_vs30    → Vertex Shader 3.0
```
- **GPU** : GeForce 6800+, Radeon X1800+
- **Limites** : Instructions dynamiques illimitées
- **Usage** : Shaders avancés, rarement dans Source

---

## 📊 Comparaison des versions

| Version | Instructions | Registres | Textures | Usage Source |
|---------|--------------|-----------|----------|--------------|
| SM 1.1  | 8-16         | 2-8       | 4        | Fallback     |
| SM 2.0  | 96           | 32        | 16       | Standard     |
| SM 2.0b | 512          | 32        | 16       | Recommandé   |
| SM 3.0  | Illimité     | Illimité  | 16+      | Avancé       |

---

## 🎮 Dans Source Engine

### Ordre de fallback (si GPU ne supporte pas)
```
ps30 → ps20b → ps20 → ps14 → ps11 → échoue
```

Le moteur charge **automatiquement** la meilleure version supportée par le GPU.

---

## 📁 Extensions de fichiers

### `.fxc` (HLSL Source)
```
monshader_ps20.fxc   → Code source HLSL
```
- Format texte lisible
- Doit être compilé

### `.vcs` (Compiled Shader)
```
monshader_ps20.vcs   → Bytecode compilé
```
- Format binaire
- Prêt à être utilisé par le moteur

### `.psh` / `.vsh` (Legacy)
```
BlurFilter_ps11.psh  → Ancien format assembleur
```
- Format assembleur Direct3D
- Utilisé avant HLSL

---

## ✅ Convention recommandée pour vos shaders

### Pour un shader moderne :

#### Pixel Shader
```
monshader_ps20.fxc    → Version de base (SM 2.0)
monshader_ps20b.fxc   → Version améliorée (SM 2.0b)
monshader_ps30.fxc    → Version avancée (SM 3.0) [optionnel]
```

#### Vertex Shader
```
monshader_vs20.fxc    → Version standard
monshader_vs30.fxc    → Version avancée [optionnel]
```

---

## 🎯 Exemples pratiques

### Shader simple (texture basique)
```
myshader_ps20.fxc     ← Suffit pour la plupart des cas
myshader_vs20.fxc
```

### Shader avec effets avancés
```
myshader_ps20b.fxc    ← Plus d'instructions disponibles
myshader_vs20.fxc
```

### Shader compatible vieux GPU
```
myshader_ps14.fxc     ← Fallback
myshader_ps20.fxc     ← Standard
myshader_ps20b.fxc    ← Moderne
myshader_vs20.fxc
```

---

## 🔍 Détection automatique dans le code C++

```cpp
SHADER_DRAW
{
    SHADOW_STATE
    {
        // Le moteur choisit automatiquement la bonne version
        if ( g_pHardwareConfig->SupportsPixelShaders_2_b() )
        {
            DECLARE_STATIC_PIXEL_SHADER( monshader_ps20b );
            SET_STATIC_PIXEL_SHADER( monshader_ps20b );
        }
        else
        {
            DECLARE_STATIC_PIXEL_SHADER( monshader_ps20 );
            SET_STATIC_PIXEL_SHADER( monshader_ps20 );
        }
    }
}
```

---

## 📌 Résumé rapide

| Suffixe | Signification | Usage |
|---------|---------------|-------|
| `_ps11` | Pixel Shader 1.1 | Très vieux GPU |
| `_ps20` | Pixel Shader 2.0 | Standard Source |
| `_ps20b` | Pixel Shader 2.0b | Recommandé |
| `_ps30` | Pixel Shader 3.0 | Avancé |
| `_vs20` | Vertex Shader 2.0 | Standard |
| `_vs30` | Vertex Shader 3.0 | Avancé |

---

## 🎨 Recommandation finale

Pour un shader moderne dans Source SDK 2013 :

```
✅ monshader_ps20b.fxc   (pixel shader optimal)
✅ monshader_vs20.fxc    (vertex shader standard)
```

C'est le **meilleur compromis** entre compatibilité et fonctionnalités ! 🚀


<a name="ressources"></a>
## 📚 Ressources

### Documentation officielle

- [Valve Developer Community](https://developer.valvesoftware.com/wiki/Main_Page)
- [Source SDK 2013 Shaders](https://developer.valvesoftware.com/wiki/Source_SDK_2013:_Shader_Authoring)
- [HLSL Reference](https://docs.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl)

### Exemples de shaders Source

Étudiez ces shaders dans `src/materialsystem/stdshaders/` :

- `lightmappedgeneric.cpp` - Shader de base pour le monde
- `vertexlitgeneric.cpp` - Shader pour les modèles
- `unlitgeneric.cpp` - Shader sans éclairage
- `water.cpp` - Eau animée
- `refract.cpp` - Réfraction


## 🎓 Exercices pratiques

### Débutant

#### Exercice 1 : Shader monochrome
**Objectif** : Créer un shader qui affiche une texture en noir et blanc

**Indice** :
```hlsl
// Convertir RGB en grayscale
float gray = dot(color.rgb, float3(0.299, 0.587, 0.114));
```

**Solution** :
```hlsl
// grayscale_ps20b.fxc
sampler BaseTextureSampler : register(s0);

struct PS_INPUT
{
    float2 vTexCoord0 : TEXCOORD0;
};

float4 main(PS_INPUT i) : COLOR
{
    float4 color = tex2D(BaseTextureSampler, i.vTexCoord0);
    
    // Conversion en niveaux de gris (formule luminance)
    float gray = dot(color.rgb, float3(0.299, 0.587, 0.114));
    
    return float4(gray, gray, gray, color.a);
}
```

#### Exercice 2 : Shader avec teinte personnalisée
**Objectif** : Ajouter un paramètre VMT pour colorer la texture

**VMT attendu** :
```vmt
"TintShader"
{
    "$basetexture" "custom/test"
    "$tintcolor" "[1 0.5 0]"  // Orange
}
```

**Solution C++** :
```cpp
BEGIN_SHADER_PARAMS
    SHADER_PARAM(BASETEXTURE, SHADER_PARAM_TYPE_TEXTURE, "shadertest/BaseTexture", "Base texture")
    SHADER_PARAM(TINTCOLOR, SHADER_PARAM_TYPE_COLOR, "[1 1 1]", "Tint color")
END_SHADER_PARAMS

// Dans DYNAMIC_STATE
float tint[4];
params[TINTCOLOR]->GetVecValue(tint, 3);
tint[3] = 1.0f;
pShaderAPI->SetPixelShaderConstant(0, tint);
```

**Solution HLSL** :
```hlsl
sampler BaseTextureSampler : register(s0);
const float3 g_TintColor : register(c0);

float4 main(PS_INPUT i) : COLOR
{
    float4 color = tex2D(BaseTextureSampler, i.vTexCoord0);
    color.rgb *= g_TintColor;
    return color;
}
```

---

### Niveau Intermédiaire

#### Exercice 3 : UV Scrolling (texture animée)
**Objectif** : Faire défiler une texture automatiquement

**Indice** : Utilisez le temps du jeu pour animer les UV

**Solution Vertex Shader** :
```hlsl
// scrolling_vs20.fxc
const float4x4 cModelViewProj : register(c0);
const float g_Time : register(c20);
const float2 g_ScrollSpeed : register(c21);  // Vitesse X, Y

struct VS_INPUT
{
    float3 vPos : POSITION;
    float2 vTexCoord0 : TEXCOORD0;
};

struct VS_OUTPUT
{
    float4 vPosition : POSITION;
    float2 vTexCoord0 : TEXCOORD0;
};

VS_OUTPUT main(const VS_INPUT v)
{
    VS_OUTPUT o;
    
    o.vPosition = mul(float4(v.vPos, 1.0), cModelViewProj);
    
    // Animer les UV
    o.vTexCoord0 = v.vTexCoord0 + g_ScrollSpeed * g_Time;
    
    return o;
}
```

**Code C++** :
```cpp
// Dans DYNAMIC_STATE
float scrollSpeed[4] = { 0.1f, 0.05f, 0.0f, 0.0f };
pShaderAPI->SetVertexShaderConstant(21, scrollSpeed);

float time = pShaderAPI->CurrentTime();
pShaderAPI->SetVertexShaderConstant(20, &time, 1);
```

#### Exercice 4 : Fresnel Effect (reflet sur les bords)
**Objectif** : Créer un effet de reflet qui s'intensifie sur les bords

**Formule Fresnel** :
```
fresnel = pow(1 - dot(viewDir, normal), power)
```

**Solution complète** :
```hlsl
// fresnel_ps20b.fxc
sampler BaseTextureSampler : register(s0);

const float3 g_CameraPos : register(c0);
const float3 g_FresnelColor : register(c1);
const float g_FresnelPower : register(c2);

struct PS_INPUT
{
    float2 vTexCoord0 : TEXCOORD0;
    float3 vWorldPos : TEXCOORD1;
    float3 vWorldNormal : TEXCOORD2;
};

float4 main(PS_INPUT i) : COLOR
{
    float4 baseColor = tex2D(BaseTextureSampler, i.vTexCoord0);
    
    // Calculer la direction de vue
    float3 viewDir = normalize(g_CameraPos - i.vWorldPos);
    float3 normal = normalize(i.vWorldNormal);
    
    // Effet Fresnel
    float fresnel = pow(1.0 - saturate(dot(viewDir, normal)), g_FresnelPower);
    
    // Mélanger avec la couleur Fresnel
    baseColor.rgb = lerp(baseColor.rgb, g_FresnelColor, fresnel);
    
    return baseColor;
}
```

---

### Niveau Avancé

#### Exercice 5 : Parallax Mapping
**Objectif** : Créer un effet de relief sans géométrie supplémentaire

**Solution** :
```hlsl
// parallax_ps20b.fxc
sampler BaseTextureSampler : register(s0);
sampler HeightMapSampler : register(s1);

const float3 g_CameraPos : register(c0);
const float g_ParallaxScale : register(c1);

struct PS_INPUT
{
    float2 vTexCoord0 : TEXCOORD0;
    float3 vWorldPos : TEXCOORD1;
    float3 vTangent : TEXCOORD2;
    float3 vBinormal : TEXCOORD3;
    float3 vNormal : TEXCOORD4;
};

float4 main(PS_INPUT i) : COLOR
{
    // Construire la matrice TBN (tangent space)
    float3x3 TBN = float3x3(
        normalize(i.vTangent),
        normalize(i.vBinormal),
        normalize(i.vNormal)
    );
    
    // Direction de vue en tangent space
    float3 viewDir = normalize(g_CameraPos - i.vWorldPos);
    float3 viewDirTS = mul(TBN, viewDir);
    
    // Échantillonner la heightmap
    float height = tex2D(HeightMapSampler, i.vTexCoord0).r;
    
    // Offset UV basé sur la hauteur
    float2 parallaxOffset = viewDirTS.xy * (height * g_ParallaxScale);
    float2 finalUV = i.vTexCoord0 + parallaxOffset;
    
    // Échantillonner avec les UV décalées
    float4 color = tex2D(BaseTextureSampler, finalUV);
    
    return color;
}
```

#### Exercice 6 : Cel Shading (Toon Shader)
**Objectif** : Créer un rendu cartoon avec des bandes d'ombres discrètes

**Solution** :
```hlsl
// celshading_ps20b.fxc
sampler BaseTextureSampler : register(s0);

const float3 g_LightDir : register(c0);
const float g_Bands : register(c1);  // Nombre de bandes (ex: 3.0)

struct PS_INPUT
{
    float2 vTexCoord0 : TEXCOORD0;
    float3 vWorldNormal : TEXCOORD1;
};

float4 main(PS_INPUT i) : COLOR
{
    float4 baseColor = tex2D(BaseTextureSampler, i.vTexCoord0);
    
    float3 normal = normalize(i.vWorldNormal);
    float ndotl = dot(normal, g_LightDir);
    
    // Quantifier l'éclairage en bandes discrètes
    float lighting = floor(ndotl * g_Bands) / g_Bands;
    lighting = saturate(lighting);
    
    // Ajouter une lumière ambiante minimale
    lighting = max(lighting, 0.3);
    
    baseColor.rgb *= lighting;
    
    // Optionnel: Contour noir
    float edge = step(0.1, ndotl);
    baseColor.rgb *= edge;
    
    return baseColor;
}
```

---

## ❓ FAQ (Foire Aux Questions)

### Questions générales

#### Q1 : Mon shader ne compile pas, que faire ?
**R:** Vérifiez :
1. Les fichiers `.fxc` sont bien dans `src/materialsystem/stdshaders/`
2. Ils sont listés dans `stdshader_dx9_20b.txt`
3. Perl est installé et dans le PATH
4. DirectX SDK est installé
5. Regardez les erreurs dans la console de compilation

#### Q2 : Mon shader compile mais la texture est invisible ?
**R:** Causes communes :
1. Le fichier `.cpp` n'est pas ajouté au projet Visual Studio
2. La DLL `stdshader_dx9.dll` n'est pas copiée dans `game/bin/`
3. Les fichiers `.vcs` ne sont pas dans `game/shaders/fxc/`
4. Le nom dans le VMT ne correspond pas au nom dans `BEGIN_VS_SHADER()`
5. Le fichier `.vtf` de texture n'existe pas

#### Q3 : Comment débugger un shader ?
**R:** Méthodes :
```hlsl
// Afficher une valeur comme couleur
return float4(value, value, value, 1);

// Afficher les UV
return float4(uv.x, uv.y, 0, 1);

// Afficher les normales
return float4(normal * 0.5 + 0.5, 1);
```

Utilisez aussi : `mat_debug 1` dans la console

#### Q4 : Quelle est la différence entre SHADOW_STATE et DYNAMIC_STATE ?
**R:**
- **SHADOW_STATE** : Configuration qui ne change pas par frame (format vertex, shaders statiques)
- **DYNAMIC_STATE** : Configuration qui change chaque frame (constantes, textures)

#### Q5 : Combien de textures puis-je utiliser ?
**R:** Maximum 16 textures (s0 à s15) en Shader Model 2.0, mais moins = meilleur performance. Visez 2-4 textures pour un bon équilibre.

---

### Questions techniques HLSL

#### Q6 : Comment faire une texture transparente ?
**R:**
```cpp
// Dans C++ (SHADOW_STATE)
pShaderShadow->EnableBlending(true);
pShaderShadow->BlendFunc(SHADER_BLEND_SRC_ALPHA, SHADER_BLEND_ONE_MINUS_SRC_ALPHA);
```
```hlsl
// Dans HLSL
float4 color = tex2D(sampler, uv);
color.a = 0.5;  // Semi-transparent
return color;
```

#### Q7 : Comment accéder au temps du jeu ?
**R:**
```cpp
// Dans C++ (DYNAMIC_STATE)
float time = pShaderAPI->CurrentTime();
pShaderAPI->SetVertexShaderConstant(20, &time, 1);
```
```hlsl
// Dans HLSL
const float g_Time : register(c20);
```

#### Q8 : Comment normaliser un vecteur en HLSL ?
**R:**
```hlsl
float3 normalized = normalize(vector);

// Ou manuellement :
float3 normalized = vector / length(vector);

// Ou plus rapide (si déjà presque normalisé) :
float3 normalized = vector * rsqrt(dot(vector, vector));
```

#### Q9 : Quelle est la différence entre tex2D et tex2Dlod ?
**R:**
- `tex2D(sampler, uv)` : Échantillonnage normal avec mipmaps automatiques
- `tex2Dlod(sampler, float4(uv, 0, lod))` : Échantillonnage avec niveau de mipmap spécifique

#### Q10 : Comment créer un shader à deux passes ?
**R:**
```cpp
SHADER_DRAW
{
    // Première passe
    SHADOW_STATE { /* config */ }
    DYNAMIC_STATE { /* état 1 */ }
    Draw();
    
    // Deuxième passe
    SHADOW_STATE { /* config */ }
    DYNAMIC_STATE { /* état 2 */ }
    Draw();
}
```

---

### Questions C++

#### Q11 : Comment charger une texture depuis un paramètre ?
**R:**
```cpp
SHADER_INIT
{
    if (params[BASETEXTURE]->IsDefined())
    {
        LoadTexture(BASETEXTURE);
    }
}

DYNAMIC_STATE
{
    BindTexture(SHADER_SAMPLER0, BASETEXTURE, FRAME);
}
```

#### Q12 : Comment passer une couleur du VMT au shader ?
**R:**
```cpp
// Définir le paramètre
SHADER_PARAM(MYCOLOR, SHADER_PARAM_TYPE_COLOR, "[1 0 0]", "My color")

// L'envoyer au shader
float color[4];
params[MYCOLOR]->GetVecValue(color, 3);
color[3] = 1.0f;
pShaderAPI->SetPixelShaderConstant(0, color);
```

#### Q13 : Comment obtenir la position de la caméra ?
**R:**
```cpp
float cameraPos[4];
pShaderAPI->GetWorldSpaceCameraPosition(cameraPos);
pShaderAPI->SetPixelShaderConstant(0, cameraPos);
```

#### Q14 : Comment utiliser des combos de shader ?
**R:**
```cpp
// Définir un combo statique
DECLARE_STATIC_PIXEL_SHADER(myshader_ps20b);
SET_STATIC_PIXEL_SHADER_COMBO(NORMALMAP, params[NORMALMAP]->IsTexture() ? 1 : 0);
SET_STATIC_PIXEL_SHADER(myshader_ps20b);

// Définir un combo dynamique
DECLARE_DYNAMIC_PIXEL_SHADER(myshader_ps20b);
SET_DYNAMIC_PIXEL_SHADER_COMBO(SKINNING, numBones > 0 ? 1 : 0);
SET_DYNAMIC_PIXEL_SHADER(myshader_ps20b);
```

Dans le `.fxc`, vous devez définir les combos :
```hlsl
// STATIC: NORMALMAP [0..1]
// DYNAMIC: SKINNING [0..1]
```

#### Q15 : Comment faire un shader qui fonctionne sur les props et le monde ?
**R:** Utilisez le format vertex approprié :
```cpp
// Pour le monde (lightmapped)
int fmt = VERTEX_POSITION | VERTEX_NORMAL | VERTEX_TEXCOORD_SIZE(0,2) | VERTEX_TEXCOORD_SIZE(1,2);

// Pour les props (vertex lit)
int fmt = VERTEX_POSITION | VERTEX_NORMAL | VERTEX_COLOR | VERTEX_TEXCOORD_SIZE(0,2);
```

---

## 🔧 Problèmes courants et solutions

### Problème : "Can't find shader .vcs"
**Solution :**
1. Vérifiez que les `.vcs` sont dans `game/shaders/fxc/`
2. Le nom du fichier doit correspondre exactement au nom dans le `.cpp`
3. Rechargez : `mat_reloadallmaterials`

### Problème : Crash au lancement avec le shader
**Solution :**
1. Compilez en **Release**, pas Debug
2. Vérifiez que la version MP/SP correspond à votre jeu
3. Vérifiez qu'il n'y a pas d'erreur dans `SHADER_INIT`

### Problème : Texture noire / blanche
**Solutions possibles :**
```cpp
// Vérifier que la texture est bien bindée
BindTexture(SHADER_SAMPLER0, BASETEXTURE, FRAME);

// Vérifier le format vertex
int fmt = VERTEX_POSITION | VERTEX_NORMAL;  // Minimal requis

// Vérifier dans le pixel shader
return float4(1, 0, 1, 1);  // Magenta = debug
```

### Problème : Performance médiocre
**Optimisations :**
1. Réduire le nombre de samplers (textures)
2. Éviter les boucles dans le pixel shader
3. Précalculer dans le vertex shader
4. Utiliser `saturate()` au lieu de `clamp(x, 0, 1)`
5. Utiliser `rsqrt()` au lieu de `1/sqrt()`

### Problème : Shader ne supporte pas shader model 2.0b
**Solution : Créer un fallback**
```cpp
SHADOW_STATE
{
    if (g_pHardwareConfig->SupportsPixelShaders_2_b())
    {
        DECLARE_STATIC_PIXEL_SHADER(myshader_ps20b);
        SET_STATIC_PIXEL_SHADER(myshader_ps20b);
    }
    else
    {
        DECLARE_STATIC_PIXEL_SHADER(myshader_ps20);
        SET_STATIC_PIXEL_SHADER(myshader_ps20);
    }
}
```

---

## 🎨 Galerie d'effets

### Effet 1 : Hologramme
```hlsl
// hologram_ps20b.fxc
sampler BaseTextureSampler : register(s0);
const float g_Time : register(c0);

float4 main(PS_INPUT i) : COLOR
{
    float4 color = tex2D(BaseTextureSampler, i.vTexCoord0);
    
    // Lignes de scan
    float scanline = sin(i.vTexCoord0.y * 100.0 + g_Time * 10.0) * 0.5 + 0.5;
    
    // Glitch aléatoire
    float glitch = step(0.98, sin(g_Time * 50.0));
    float2 glitchOffset = float2(glitch * 0.1, 0);
    
    color.rgb *= 0.5 + scanline * 0.5;
    color.rgb = lerp(color.rgb, float3(0, 1, 1), 0.3);  // Teinte cyan
    color.a *= 0.7;  // Semi-transparent
    
    return color;
}
```

### Effet 2 : Force Field
```hlsl
// forcefield_ps20b.fxc
sampler NoiseSampler : register(s0);
const float3 g_CameraPos : register(c0);
const float g_Time : register(c1);

float4 main(PS_INPUT i) : COLOR
{
    // Vue direction
    float3 viewDir = normalize(g_CameraPos - i.vWorldPos);
    float3 normal = normalize(i.vWorldNormal);
    
    // Fresnel
    float fresnel = pow(1.0 - abs(dot(viewDir, normal)), 3.0);
    
    // Texture de bruit animée
    float2 noiseUV = i.vTexCoord0 * 2.0 + float2(g_Time * 0.1, 0);
    float noise = tex2D(NoiseSampler, noiseUV).r;
    
    // Hexagones (pattern)
    float pattern = step(0.5, frac(noise * 10.0));
    
    // Couleur finale
    float3 color = float3(0.2, 0.5, 1.0) * fresnel;
    color += pattern * 0.3;
    
    return float4(color, fresnel * 0.8);
}
```

### Effet 3 : Glowing Edges (Sobel)
```hlsl
// glow_edges_ps20b.fxc
sampler BaseTextureSampler : register(s0);
const float2 g_TexelSize : register(c0);  // 1/résolution

float4 main(PS_INPUT i) : COLOR
{
    // Échantillonner 9 pixels (kernel 3x3)
    float2 offsets[9] = {
        float2(-1,-1), float2(0,-1), float2(1,-1),
        float2(-1, 0), float2(0, 0), float2(1, 0),
        float2(-1, 1), float2(0, 1), float2(1, 1)
    };
    
    // Sobel X
    float sobelX[9] = {-1, 0, 1, -2, 0, 2, -1, 0, 1};
    
    // Sobel Y
    float sobelY[9] = {-1, -2, -1, 0, 0, 0, 1, 2, 1};
    
    float edgeX = 0;
    float edgeY = 0;
    
    for (int j = 0; j < 9; j++)
    {
        float2 uv = i.vTexCoord0 + offsets[j] * g_TexelSize;
        float gray = dot(tex2D(BaseTextureSampler, uv).rgb, float3(0.299, 0.587, 0.114));
        
        edgeX += gray * sobelX[j];
        edgeY += gray * sobelY[j];
    }
    
    float edge = sqrt(edgeX * edgeX + edgeY * edgeY);
    
    float4 baseColor = tex2D(BaseTextureSampler, i.vTexCoord0);
    
    // Glow sur les bords
    float3 glowColor = float3(0, 1, 1);
    baseColor.rgb += glowColor * edge;
    
    return baseColor;
}
```

---

## 📖 Glossaire

**Alpha** : Canal de transparence (0 = transparent, 1 = opaque)

**Blending** : Mélange de couleurs entre surfaces transparentes

**Combo** : Variation d'un shader avec différentes fonctionnalités activées/désactivées

**Constant Register** : Emplacement mémoire pour passer des données CPU → GPU

**Culling** : Masquer les faces arrière des polygones (optimisation)

**Fragment** : Synonyme de pixel dans le contexte des shaders

**Fresnel** : Effet où les bords d'un objet réfléchissent plus la lumière

**HLSL** : High Level Shader Language (DirectX)

**Interpolation** : Calcul des valeurs entre vertices (lissage)

**Lambert** : Modèle d'éclairage diffus simple (dot product)

**Mipmap** : Versions pré-calculées d'une texture à différentes résolutions

**Normal Map** : Texture contenant des informations de relief

**Parallax** : Technique pour simuler du relief sans géométrie

**Register** : Emplacement pour stocker des données dans le shader

**Sampler** : Objet pour lire une texture

**Saturate** : Limiter une valeur entre 0 et 1

**Semantic** : Annotation indiquant l'usage d'une variable (POSITION, TEXCOORD, etc.)

**Swizzle** : Réorganisation de composants (ex: `color.rgb`, `pos.xyz`)

**Tangent Space** : Espace de coordonnées local à la surface

**UV** : Coordonnées de texture 2D (U = X, V = Y)

**Vertex** : Point dans l'espace 3D (sommet)

**VMT** : Valve Material Type (fichier de définition de matériau)

**VTF** : Valve Texture Format (format de texture Source)

---

## 🚀 Prochaines étapes

Maintenant que vous avez toutes les connaissances nécessaires :

1. ✅ Commencez par un shader simple (texture + couleur)
2. ✅ Ajoutez progressivement des fonctionnalités
3. ✅ Étudiez les shaders de Source dans `stdshaders/`
4. ✅ Expérimentez avec les exemples de ce guide
5. ✅ Créez vos propres effets uniques !

**Bon courage et amusez-vous bien ! 🎨**

---

*Cette documentation a été créée pour vous aider à maîtriser la création de shaders dans Source Engine. N'hésitez pas à expérimenter et à partager vos créations avec la communauté !*
