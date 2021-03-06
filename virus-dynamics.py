import random
import pylab


class NoChildException(Exception):
    """
    Indicates that a virus particle does not reproduce.
    """


class SimpleVirus(object):
    """
    Representation of a simple virus (does not model drug effects/resistance).
    """

    def __init__(self, maxBirthProb, clearProb):
        """
        Initialize a SimpleVirus instance, saves all parameters as attributes of the instance.

        maxBirthProb: Maximum reproduction probability (a float between 0-1)

        clearProb: Maximum clearance probability (a float between 0-1)
        """
        self.maxBirthProb = maxBirthProb
        self.clearProb = clearProb

    def getMaxBirthProb(self):
        """
        returns: the max birth probability.
        """
        return self.maxBirthProb

    def getClearProb(self):
        """
        returns: the clear probability.
        """
        return self.clearProb

    def doesClear(self):
        """
        Stochastically determines whether this virus particle is cleared from the patient's body at a time step.

        returns: True with probability self.getClearProb and otherwise returns False
        """
        if random.random() <= self.getClearProb():
            return True
        else:
            return False

    def reproduce(self, popDensity):
        """
        Stochastically determines whether this virus particle reproduces at a time step. Called by the update()
        method in the Patient and TreatedPatient classes. The virus particle reproduces with probability:
        self.maxBirthProb * (1 - popDensity).
        
        If this virus particle reproduces, then reproduce() creates and returns the instance of the offspring
        SimpleVirus (which has the same maxBirthProb and clearProb values as its parent).

        popDensity: the population density (a float), defined as the current irus population divided by the
        maximum population.

        returns: a new instance of the SimpleVirus class representing the offspring of this virus particle. The
        child should have the same maxBirthProb and clearProb values as this virus. Raises a NoChildException
        if this virus particle does not reproduce.
        """
        repProb = self.getMaxBirthProb() * (1 - popDensity)
        if random.random() <= repProb:
            # The virus reproduces
            return SimpleVirus(self.getMaxBirthProb(), self.getClearProb())
        else:
            raise NoChildException


class Patient(object):
    """
    Representation of a simplified patient. The patient does not take any drugs and his/her virus populations have
    no drug resistance.
    """

    def __init__(self, viruses, maxPop):
        """
        Initialization function, saves the viruses and maxPop parameters as attributes.

        viruses: the list representing the virus population (a list of SimpleVirus instances)

        maxPop: the maximum virus population for this patient (an integer)
        """
        self.viruses = viruses
        self.maxPop = maxPop

    def getViruses(self):
        """
        returns: the viruses in this Patient
        """
        return self.viruses

    def getMaxPop(self):
        """
        returns: the max virus population
        """
        return self.maxPop

    def getTotalPop(self):
        """
        returns: The total virus population (an integer)
        """
        return len(self.viruses)

    def update(self):
        """
        Update the state of the virus population in this patient for a single time step.

        returns: The total virus population at the end of the update (an integer)
        """
        # Determine whether each virus particle survives and updates the list of virus particles accordingly
        viruses_survived = self.getViruses()[:]
        for virus in self.getViruses():
            if virus.doesClear():
                viruses_survived.remove(virus)
        self.viruses = viruses_survived

        # Determine population density (which is used until next update)
        popDensity = self.getTotalPop() / self.getMaxPop()

        # Determine which virus particle should reproduce and add offspring to list of viruses affecting patient
        viruses_produced = []
        for virus in self.getViruses():
            try:
                viruses_produced.append(virus.reproduce(popDensity))
            except NoChildException:
                pass

        self.viruses += viruses_produced

        return self.getTotalPop()


def simulationWithoutDrug(numViruses, maxPop, maxBirthProb, clearProb,
                          numTrials):
    """
    Runs a simulation and plots a graph (no drugs are used, viruses do not have any drug resistance).
    For each of numTrials trial, instantiates a patient, runs a simulation for 300 timesteps, and plots the average
    virus population size as a function of time.

    numViruses: number of SimpleVirus to create for patient (an integer)

    maxPop: maximum virus population for patient (an integer)

    maxBirthProb: Maximum reproduction probability (a float between 0-1)

    clearProb: Maximum clearance probability (a float between 0-1)

    numTrials: number of simulation runs to execute (an integer)
    """
    numTimeSteps = 300

    virusPop = []
    for time in range(numTimeSteps):
        virusPop.append(0)

    for trial in range(numTrials):
        sim_viruses = []
        for virus in range(numViruses):
            sim_viruses.append(SimpleVirus(maxBirthProb, clearProb))
        sim_patient = Patient(sim_viruses, maxPop)

        for time in range(numTimeSteps):
            virusPop[time] += sim_patient.update()

    for time in range(numTimeSteps):
        virusPop[time] /= numTrials

    timeSteps = []
    for time in range(numTimeSteps):
        timeSteps.append(time)

    pylab.title("Virus simulation without drugs averaged over " + str(numTrials) + " trial(s)")
    pylab.legend()
    pylab.xlabel("Time")
    pylab.ylabel("Virus population")
    pylab.plot(virusPop)
    pylab.show()


class ResistantVirus(SimpleVirus):
    """
    Representation of a virus which can have drug resistance.
    """

    def __init__(self, maxBirthProb, clearProb, resistances, mutProb):
        """
        Initialize a ResistantVirus instance, saves all parameters as attributes of the instance.

        maxBirthProb: Maximum reproduction probability (a float between 0-1)

        clearProb: Maximum clearance probability (a float between 0-1)

        resistances: A dictionary of drug names (strings) mapping to the state of this virus particle's resistance
        (either True or False) to each drug. e.g. {'oseltamivir':False, 'zanamivir':False}, means that this virus
        particle is resistant to neither oseltamivir nor zanamivir.

        mutProb: Mutation probability for this virus particle (a float). This is the probability of the offspring
        acquiring or losing resistance to a drug.
        """
        super().__init__(maxBirthProb, clearProb)
        self.resistances = resistances
        self.mutProb = mutProb

    def getResistances(self):
        """
        returns: the resistances for this virus
        """
        return self.resistances

    def getMutProb(self):
        """
        returns: the mutation probability for this virus
        """
        return self.mutProb

    def isResistantTo(self, drug):
        """
        Get the state of this virus particle's resistance to a drug. This method is called by getResistPop() in
        TreatedPatient to determine how many virus particles have resistance to a drug.

        drug: The drug (a string)

        returns: True if this virus instance is resistant to the drug, False otherwise
        """
        return self.resistances.get(drug)

    def reproduce(self, popDensity, activeDrugs):
        """
        Stochastically determines whether this virus particle reproduces at a time step. Called by the update()
        method in the TreatedPatient class.

        A virus particle will only reproduce if it is resistant to ALL the drugs in the activeDrugs list. For example,
        if there are 2 drugs in the activeDrugs list, and the virus particle is resistant to 1 or no drugs,
        then it will NOT reproduce.

        Hence, if the virus is resistant to all drugs in activeDrugs, then the virus reproduces with probability:
        self.maxBirthProb * (1 - popDensity).

        If this virus particle reproduces, then reproduce() creates and returns the instance of the offspring
        ResistantVirus (which has the same maxBirthProb and clearProb values as its parent). The offspring virus
        will have the same maxBirthProb, clearProb, and mutProb as the parent.

        For each drug resistance trait of the virus (i.e. each key of self.resistances), the offspring has
        probability 1-mutProb of inheriting that resistance trait from the parent, and probability mutProb of
        switching that resistance trait in the offspring.

        For example, if a virus particle is resistant to oseltamivir but not zanamivir, and self.mutProb is 0.1,
        then there is a 10% chance that that the offspring will lose resistance to oseltamivir and a 90% chance that
        the offspring will be resistant to oseltamivir. There is also a 10% chance that the offspring will gain
        resistance to zanamivir and a 90% chance that the offspring will not be resistant to zanamivir.

        popDensity: the population density (a float), defined as the current virus population divided by the
        maximum population

        activeDrugs: a list of the drug names acting on this virus particle (a list of strings)

        returns: a new instance of the ResistantVirus class representing the offspring of this virus particle. The
        child should have the same maxBirthProb and clearProb values as this virus. Raises a NoChildException if this
        virus particle does not reproduce.
        """
        drugsAreEffective = False
        for drug in activeDrugs:
            if not self.isResistantTo(drug):
                drugsAreEffective = True

        if drugsAreEffective:
            raise NoChildException
        else:
            repProb = self.getMaxBirthProb() * (1 - popDensity)
            if random.random() <= repProb:
                # Mutations might occur
                newResistances = self.getResistances().copy()
                for drug in newResistances.keys():
                    if random.random() <= self.getMutProb():
                        newResistances[drug] = not newResistances[drug]
                # The virus reproduces
                return ResistantVirus(self.getMaxBirthProb(), self.getClearProb(), newResistances, self.getMutProb())
            else:
                raise NoChildException


class TreatedPatient(Patient):
    """
    Representation of a patient. The patient is able to take drugs and his/her virus population can acquire resistance
    to the drugs he/she takes.
    """

    def __init__(self, viruses, maxPop):
        """
        Initialization function, saves the viruses and maxPop parameters as attributes. Also initializes the list of
        drugs being administered (which should initially include no drugs).

        viruses: The list representing the virus population (a list of virus instances)

        maxPop: The  maximum virus population for this patient (an integer)
        """
        super().__init__(viruses, maxPop)
        self.prescriptions = []

    def addPrescription(self, newDrug):
        """
        Administer a drug to this patient. After a prescription is added, the drug acts on the virus population for
        all subsequent time steps. If the newDrug is already prescribed to this patient, the method has no effect.

        newDrug: The name of the drug to administer to the patient (a string)
        """
        if newDrug not in self.getPrescriptions():
            self.prescriptions.append(newDrug)

    def getPrescriptions(self):
        """
        returns: The list of drug names (strings) being administered to this patient
        """
        return self.prescriptions

    def getResistPop(self, drugResist):
        """
        Get the population of virus particles resistant to the drugs listed in drugResist.

        drugResist: Which drug resistances to include in the population (a list of strings - e.g. ['oseltamivir']
        or ['oseltamivir', 'zanamivir'])

        returns: The population of viruses (an integer) with resistances to all drugs in the drugResist list
        """
        numResistantViruses = 0
        for virus in self.getViruses():
            if len(drugResist) > 0:
                virusIsResistant = True
                for drug in drugResist:
                    if not virus.isResistantTo(drug):
                        virusIsResistant = False
                if virusIsResistant:
                    numResistantViruses += 1
        return numResistantViruses

    def update(self):
        """
        Update the state of the virus population in this patient for a single time step.

        returns: The total virus population at the end of the update (an integer)
        """
        # Determine whether each virus particle survives and updates the list of virus particles accordingly
        viruses_survived = self.getViruses()[:]
        for virus in self.getViruses():
            if virus.doesClear():
                viruses_survived.remove(virus)
        self.viruses = viruses_survived

        # Determine population density (which is used until next update)
        popDensity = self.getTotalPop() / self.getMaxPop()

        # Determine which virus particle should reproduce and add offspring to list of viruses affecting patient
        viruses_produced = []
        for virus in self.getViruses():
            try:
                # Account for the list of drugs in the determination of whether each virus particle reproduces
                viruses_produced.append(virus.reproduce(popDensity, self.getPrescriptions()))
            except NoChildException:
                pass

        self.viruses += viruses_produced

        return self.getTotalPop()


def simulationWithDrug(numViruses, maxPop, maxBirthProb, clearProb, resistances, mutProb, numTrials):
    """
    Runs a simulation and plots a graph.

    For each of numTrials trials, instantiates a patient, runs a simulation for 150 timesteps, adds oseltamivir, 
    and runs the simulation for an additional 150 timesteps. At the end plots the average virus population size 
    (for both the total virus population and the oseltamivir-resistant virus population) as a function of time.

    numViruses: number of ResistantVirus to create for patient (an integer)

    maxPop: maximum virus population for patient (an integer)

    maxBirthProb: Maximum reproduction probability (a float between 0-1)

    clearProb: maximum clearance probability (a float between 0-1)

    resistances: a dictionary of drugs that each ResistantVirus is resistant to (e.g., {'oseltamivir': False})

    mutProb: mutation probability for each ResistantVirus particle (a float between 0-1)

    numTrials: number of simulation runs to execute (an integer)
    """
    numTimeSteps = 300
    drugAdminTime = 150
    drugToAdmin = 'oseltamivir'

    totalVirusPop = []
    resistantVirusPop = []
    for time in range(numTimeSteps):
        totalVirusPop.append(0)
        resistantVirusPop.append(0)

    for trial in range(numTrials):
        sim_viruses = []
        for virus in range(numViruses):
            sim_viruses.append(ResistantVirus(maxBirthProb, clearProb, resistances, mutProb))
        sim_patient = TreatedPatient(sim_viruses, maxPop)

        for time in range(numTimeSteps):
            if time == drugAdminTime:
                sim_patient.addPrescription(drugToAdmin)
            totalVirusPop[time] += sim_patient.update()
            resistantVirusPop[time] += sim_patient.getResistPop(resistances)

    for time in range(numTimeSteps):
        totalVirusPop[time] /= numTrials
        resistantVirusPop[time] /= numTrials

    pylab.title("Virus simulation averaged over " + str(numTrials) + " trial(s); drug administered at time " +
                str(drugAdminTime))
    pylab.xlabel("Time")
    pylab.ylabel("Virus population")
    pylab.plot(totalVirusPop, label="Total virus population")
    pylab.plot(resistantVirusPop, label="Resistant virus population")
    pylab.legend()
    pylab.show()


# First simulate a simple virus without any drug treatment
numViruses = 100
maxPop = 1000
maxBirthProb = 0.1
clearProb = 0.05
numTrials = 100
simulationWithoutDrug(numViruses, maxPop, maxBirthProb, clearProb, numTrials)

# Next, simulate drug treatment (starting at time 150) on a virus that can mutate a resistance
resistances = {'oseltamivir': False}
mutProb = 0.005
simulationWithDrug(numViruses, maxPop, maxBirthProb, clearProb, resistances, mutProb, numTrials)
