import os
import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from GeneratorInterface.EvtGenInterface.EvtGenSetting_cff import *
from Configuration.Generator.Pythia8PhotonFluxSettings_cfi import PhotonFlux_PbPb

# Inclusive SoftQCD photoproduction, no pTHatMin cut; photon from Beam A.
# CR mode 2: gluon-move model (PYTHIA calls mode 1 the QCD-based model).
# Process, beam, CR mode and pTHatMin are fixed for this production.
# Only the original GENFRAG_PDF and GENFRAG_MPI_SCALE overrides are retained.
pdfSetTarget = os.environ.get('GENFRAG_PDF', 'LHAPDF6:EPPS21nlo_CT18Anlo_Pb208')
mpiScale = float(os.environ.get('GENFRAG_MPI_SCALE', '3.0'))

processParameters = [
    'SoftQCD:all = on',
    'HardQCD:all = off',
    'PhotonParton:all = off',
    'Photon:ProcessType = 0',
    'ColourReconnection:reconnect = on',
    'ColourReconnection:mode = 2',
    # No explicit resolved/direct selection; SoftQCD supplies hadronic photon events.
    'MultipartonInteractions:pT0Ref = ' + str(mpiScale),
    'PDF:beamA2gamma = on',
    'PDF:beamB2gamma = off',
    'PDF:proton2gammaSet = 0',
    'PDF:pSetB = ' + pdfSetTarget,  # hadronic target is Beam B
    'PDF:gammaFluxApprox2bMin = 13.272',
    'PDF:beam2gammaApprox = 2',
    'Photon:sampleQ2 = off',
]

print('GenFrag: ' + '; '.join(processParameters))

generator = cms.EDFilter("Pythia8GeneratorFilter",
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1.0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    comEnergy = cms.double(5362.),
    PhotonFlux = PhotonFlux_PbPb,
    ExternalDecays = cms.PSet(
        EvtGen130 = cms.untracked.PSet(
            decay_table = cms.string('GeneratorInterface/EvtGenInterface/data/DECAY_2020_NOLONGLIFE.DEC'),
            operates_on_particles = cms.vint32(),
            particle_property_file = cms.FileInPath('GeneratorInterface/EvtGenInterface/data/evt_2020.pdl'),
            user_decay_file = cms.vstring('GeneratorInterface/ExternalDecays/data/D0_Kpi.dec'),
            list_forced_decays = cms.vstring('myD0', 'myanti-D0'),
            convertPythiaCodes = cms.untracked.bool(False),
        ),
        parameterSets = cms.vstring('EvtGen130')
    ),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        processParameters = cms.vstring(*processParameters),
        parameterSets = cms.vstring('pythia8CommonSettings',
                                    'processParameters')
    )
)

generator.PythiaParameters.processParameters.extend(EvtGenExtraParticles)

partonfilter = cms.EDFilter("PythiaFilter",
    ParticleID = cms.untracked.int32(4)  # c or cbar anywhere in the event (not only prompt)
)

D0Daufilter = cms.EDFilter("PythiaMomDauFilter",
    ParticleID = cms.untracked.int32(421),
    MomMinPt = cms.untracked.double(0.),
    MomMinEta = cms.untracked.double(-10),
    MomMaxEta = cms.untracked.double(10),
    DaughterIDs = cms.untracked.vint32(-321, 211),
    NumberDaughters = cms.untracked.int32(2),
    NumberDescendants = cms.untracked.int32(0),
)

ProductionFilterSequence = cms.Sequence(generator*partonfilter*D0Daufilter)
