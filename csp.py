#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
csp.py
------------

Implementación de los algoritmos más clásicos para el problema
de satisfacción de restricciones. Se define formalmente el
problema de satisfacción de restricciones y se desarrollan los
algoritmos para solucionar el problema por búsqueda.

En particular se implementan los algoritmos de forward checking y
el de arco consistencia. Así como el algoritmo de min-conflics.

En este modulo no es necesario modificar nada.
"""

import copy
import random

__author__ = 'juliowaissman'


class GrafoRestriccion(object):
    """
    Clase abstracta para hacer un grafo de restricción 

    """

    def __init__(self):
        """
        Inicializa las propiedades del grafo de restriccón

        """
        self.dominio = {}
        self.vecinos = {}
        self.backtracking = 0  # Solo para efectos de comparación

    def restriccion(self, (xi, vi), (xj, vj)):
        """
        Verifica si se cumple la restriccion binaria entre las variables xi
        y xj cuando a estas se le asignan los valores vi y vj respectivamente.

        @param xi: El nombre de una variable
        @param vi: El valor que toma la variable xi (dentro de self.dominio[xi]
        @param xj: El nombre de una variable
        @param vj: El valor que toma la variable xi (dentro de self.dominio[xj]

        @return: True si se cumple la restricción

        """ 
        raise NotImplementedError("Método a implementar")

def asignacion_grafo_restriccion(gr, ap=None, consist=1, dmax=None, traza=False) :
    """
    Asigación de una solución al grafo de restriccion si existe
    por búsqueda primero en profundidad.

    Para utilizarlo con un objeto tipo GrafoRestriccion gr:
    >>> asignacion = asignacion_grafo_restriccion(gr)

    @param gr: Un objeto tipo GrafoRestriccion
    @param ap: Un diccionario con una asignación parcial
    @param consist: Un valor 0, 1 o 2 para máximo grado de consistencia
    @param dmax: Máxima profundidad de recursión, solo por seguridad
    @param traza: Si True muestra el proceso de asignación
    
    @return: Una asignación completa (diccionario con variable:valor)
             o None si la asignación no es posible.

    """
    if ap == None:
        ap = {}

    if dmax == None:  #  Ajusta la máxima produndidad de búsqueda
        dmax = len(gr.dominio) 
    
    if traza:
        print (len(gr.dominio) - dmax) * '\t', ap

    if set(ap.keys()) == set(gr.dominio.keys()):  #  Asignación completa
        return ap.copy()
    
    var = selecciona_variable(gr, ap)

    for val in ordena_valores(gr, ap, var):
        
        dominio = consistencia(gr, ap, var, val, consist)

        if dominio is not None:
            for variable in dominio:
                gr.dominio[variable] -= dominio[variable]

            ap[var] = val
            
            apn = asignacion_grafo_restriccion(gr, ap, consist, dmax - 1, traza)

            if apn is not None:
                return apn
            else:
                del ap[var]
                for variable in dominio:
                    gr.dominio[variable] |= dominio[variable] 
    gr.backtracking += 1
    return None

def selecciona_variable(gr, ap):
    if len(ap) == 0:
        return max(gr.dominio.keys(), key=lambda v:gr.vecinos[v])
    return min([var for var in gr.dominio.keys() if var not in ap],
               key=lambda v:len(gr.dominio[v]))
    

def ordena_valores(gr, ap, xi):
    def conflictos(vi):
        acc = 0
        for xj in gr.vecinos[xi]:
            if xj not in ap:
                for vj in gr.dominio[xj]:
                    if not gr.restriccion((xi, vi), (xj, vj)):
                        acc += 1
        return acc
    return sorted(gr.dominio[xi], key=conflictos, reverse=True)

def consistencia(gr, ap, xi, vi, tipo):
    if tipo == 0:
        for (xj, vj) in ap.iteritems():
            if xj in gr.vecinos[xi] and not gr.restriccion((xi, vi), (xj, vj)):
                return None
        return {}

    dominio = {}
    if tipo == 1:
        for xj in gr.vecinos[xi]:
            if xj not in ap:
                dominio[xj] = set()
                for vj in gr.dominio[xj]:
                    if not gr.restriccion((xi, vi), (xj, vj)):
                        dominio[xj].add(vj)
                if len(dominio[xj]) == len(gr.dominio[xj]):
                    return None
        return dominio
    if tipo == 2:
        #================================================
        #   Implementar el algoritmo de AC3
        #   y probarlo con las n-reinas
        #================================================
        worklist = {(j, xi) for j in gr.vecinos[xi]}

        dominio[xi] = gr.dominio[xi] - {vi}

        while worklist:
            (i, j) = worklist.pop()
            if arc_reduce(gr, dominio, i, j):
                if dominio[i] and not gr.dominio[i] - dominio[i]:
                    return None
                else:
                    worklist |= {(i, k) for k in gr.vecinos[i] if k != j }

        return dominio

def arc_reduce(gr, dominio, x, y):
    change = False
    remove = set()
    xdom = gr.dominio[x] - (dominio[x] if x in dominio else remove)
    for vx in xdom:
        hacer_machaca = False
        ydom = gr.dominio[y] - (dominio[y] if y in dominio else set())
        for vy in ydom:
            if gr.restriccion((x, vx), (y, vy)):
                hacer_machaca = True
                break
        if not hacer_machaca:
            remove.add(vx)
            change = True
    if change:
        dominio[x] = dominio[x] | remove if x in dominio else remove
    return change


def min_conflictos(gr, rep=1000, maxit=100):
    for _ in xrange(maxit):
        a = minimos_conflictos(gr, rep)
        if a is not None:
            return a
    return None

def minimos_conflictos(gr, rep=100):
    #================================================
    #   Implementar el algoritmo de minimos conflictos
    #   y probarlo con las n-reinas
    #================================================
    

    a = {i: random.choice(list(gr.dominio[i])) for i in gr.dominio}
    b = [i for i in a.keys() if conflictos(gr, a, i, a[i])]
    for _ in xrange(rep):
        #print "a:", a
        if not b:
            return a
        i = b.pop()
        #print "a[i]", a[i]
        a[i] = min(gr.dominio[i], key=lambda x: len(conflictos(gr, a, i, x)))
        confl_i = conflictos(gr, a, i, a[i])
        if confl_i:
            b.insert(0, i)
            for j in confl_i:
                if j not in b:
                    b.append(j)
        #print "a'[i]", a[i]
        #print "b: ", b
        #print "conflictos", i, ":", conflictos((i, a[i]))
    return None

def conflictos(gr, a, xi, vi):
        acc = []
        for xj in gr.vecinos[xi]:
            if not gr.restriccion((xi, vi), (xj, a[xj])):
                acc.append(xj)
        return acc