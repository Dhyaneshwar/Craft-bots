;; domain file for assignment-1 part-2

(define (domain craft-bots-temporal)

    (:requirements :strips :typing :equality :fluents :durative-actions :conditional-effects :negative-preconditions :timed-initial-literals :disjunctive-preconditions)

    (:types
        actor node mine task color - object
    )

    (:predicates 
        (actor_location ?a - actor ?l - node)
        (connected ?l1 - node ?l2 - node)

        (mine_detail ?m - mine ?l - node ?c - color)
        (resource_location ?t -task ?l - node ?c - color)
        
        (create_site ?t - task ?l - node)
        (site_not_created ?t - task ?l - node)
        
        (carrying ?a - actor ?c - color)
        
        (deposited ?a - actor ?c - color ?l - node)
        (not_deposited ?a - actor ?c - color ?l - node)
        (not-same ?a1 ?a2 - actor)

        (is_orange ?c - color)
        (is_blue ?c - color)
        (is_red ?c - color)
        (is_black ?c - color)
        (is_green ?c - color)

        (not_orange ?c - color) 
        (not_blue ?c - color)
        (not_red ?c - color)
        (not_black ?c - color)
        (not_green ?c - color)
        
        (red_available ?c - color)

        (building_built ?t - task ?l - node)
        (building_not_built ?t - task ?l - node)
    )

    (:functions 
        (edge_length ?l1 - node ?l2 - node)
        (move_speed ?a - actor)
        (mine_duration ?m - mine)
        (mine_duration_blue ?m - mine)
        (individual_resource_required ?t - task ?c - color)
        (count_of_resource_carried ?a - actor ?c - color)
        (total_resource_required ?t - task ?l - node)
        (total_resource_in_inventory ?a - actor)
    )

    (:durative-action move_between_nodes
        :parameters (?a - actor ?l1 ?l2 - node)
        :duration (= ?duration (/ (edge_length ?l1 ?l2) (move_speed ?a)))
        :condition (and 
            (at start (actor_location ?a ?l1))
            (over all (connected ?l1 ?l2))
        )
        :effect (and
            (at start (not (actor_location ?a ?l1)))
            (at end (actor_location ?a ?l2))
        )
    )

    ;; create a new site at the node where actor is present
    (:durative-action create-site
        :parameters (?a - actor ?t - task ?l - node)
        :duration (= ?duration 1)
        :condition (and 
            (at start (site_not_created ?t ?l))
            (over all (actor_location ?a ?l))
        )
        :effect (and 
            (at start (not (site_not_created ?t ?l)))
            (at end (create_site ?t ?l))
        )
    )
    
    ;; initial-mine red, black or green resources
    (:durative-action mine
        :parameters (?a - actor ?t - task ?l - node ?c - color ?m - mine)
        ;; duration determined by the mine's max progress and actor's mining rate
        :duration (= ?duration (mine_duration ?m))
        :condition (and 
            (at start (and
                (mine_detail ?m ?l ?c) 
                (not_orange ?c) 
                (not_blue ?c)
            ))
            (over all (and 
                (actor_location ?a ?l) 
                (> (individual_resource_required ?t ?c) 0))
            )
        )
        :effect (and 
            (at end (and 
                    (resource_location ?t ?l ?c)
                )
            )
        )
    )

    ;; blue resource takes twice as long to mine
    (:durative-action mine-blue
        :parameters (?a - actor ?t - task ?l - node ?c - color ?m - mine)
        ;; duration determined by the mine's max progress and actor's mining rate
        :duration (= ?duration (mine_duration_blue ?m))
        :condition (and 
            (at start (and
                (mine_detail ?m ?l ?c) 
                (is_blue ?c)
            ))
            (over all (and 
                (actor_location ?a ?l) 
                (> (individual_resource_required ?t ?c) 0))
            )
        )
        :effect (and 
            (at end (and 
                    (resource_location ?t ?l ?c)
                )
            )
        )
    )

    ;; orange resource requires multiple actors to mine
    (:durative-action mine-orange
        :parameters (?a1 - actor ?t - task ?l - node ?c - color ?m - mine ?a2 - actor)
        :duration (= ?duration (mine_duration ?m))
        :condition (and 
            (at start (and
                (mine_detail ?m ?l ?c) 
                (is_orange ?c)

            ))
            (over all (and 
                (not-same ?a1 ?a2) 
                (actor_location ?a1 ?l) 
                (actor_location ?a2 ?l)
                (> (individual_resource_required ?t ?c) 0))
            )
        )
        :effect (and 
            (at end (and 
                    (resource_location ?t ?l ?c)
                )
            )
        )
    )

    (:durative-action pick-up
        :parameters (?a - actor ?t - task ?l - node ?c - color)
        :duration (= ?duration 1)
        :condition (and 
            (at start (and 
                (not_black ?c) 
                (not_red ?c))
            )
            (over all (and 
                    (resource_location ?t ?l ?c) 
                    (actor_location ?a ?l) 
                    (> (individual_resource_required ?t ?c) 0)
                    (< (count_of_resource_carried ?a ?c) (individual_resource_required ?t ?c))
                    (<= (total_resource_in_inventory ?a) 7)
                )
            )
        )
        :effect (and 
            (at start (and
                    (not (resource_location ?t ?l ?c)) 
                )
            )
            (at end (and 
                    (increase (count_of_resource_carried ?a ?c) 1)
                    (increase (total_resource_in_inventory ?a) 1)
                )
            )
        )
    )

    ;; red resource can only be collected within time interval 0-1200
    (:durative-action pick-up-red
        :parameters (?a - actor ?t - task ?l - node ?c - color)
        :duration (= ?duration 1)
        :condition (and 
            (at start (and 
                    (is_red ?c)
                    (red_available ?c) 
                )
            )
            (over all (and 
                    (actor_location ?a ?l)
                    (resource_location ?t ?l ?c) 
                    (> (individual_resource_required ?t ?c) 0)
                    (< (count_of_resource_carried ?a ?c) (individual_resource_required ?t ?c))
                    (<= (total_resource_in_inventory ?a) 7)
                )
            )
        )
        :effect (and
            (at start (and
                    (not (resource_location ?t ?l ?c)) 
                )
            )
            (at end (and
                    (increase (count_of_resource_carried ?a ?c) 1)
                    (increase (total_resource_in_inventory ?a) 1)
                )
            )
        )
    )
    
    ;; black resource cannot be carried with any other resource
    (:durative-action pick-up-black
        :parameters (?a - actor ?t - task ?l - node ?c - color)
        :duration (= ?duration 1)
        :condition (and 
            (at start (and 
                    (is_black ?c)
                )
            )
            (over all (and 
                    (actor_location ?a ?l) 
                    (resource_location ?t ?l ?c)
                    (> (individual_resource_required ?t ?c) 0)
                    (= (total_resource_in_inventory ?a) 0)
                )
            )
        )
        :effect (and 
            (at start (and
                    (not (resource_location ?t ?l ?c)) 
                )
            )
            (at end (and
                    (increase (count_of_resource_carried ?a ?c) 1)
                    (increase (total_resource_in_inventory ?a) 1)
                )
            )
        )
    )
    
    (:durative-action deposit
        :parameters (?a - actor ?t - task ?l - node ?c - color)
        :duration (= ?duration 1)
        :condition (and 
            (over all (and 
                    (actor_location ?a ?l) 
                    (create_site ?t ?l)
                    (> (total_resource_in_inventory ?a) 0)
                    (> (individual_resource_required ?t ?c) 0)
                    (> (count_of_resource_carried ?a ?c) 0)
                    (> (total_resource_required ?t ?l) 0)
                )
            )
        )
        :effect (and 
            (at start (and
                    (decrease (individual_resource_required ?t ?c) 1)
                    (decrease (count_of_resource_carried ?a ?c) 1)
                )
            )
            (at end (and 
                (decrease (total_resource_required ?t ?l) 1)
                (decrease (total_resource_in_inventory ?a) 1))
            )
        )
    )
            
    (:durative-action construct_building
        :parameters (?a - actor ?t - task ?l - node ?c - color)
        :duration (= ?duration 33)
        :condition (and 
            (over all (and 
                    (create_site ?t ?l) 
                    (actor_location ?a ?l) 
                    (= (total_resource_required ?t ?l) 0)
                    (building_not_built ?t ?l)
                )
            )
        )
        :effect (and 
            (at end (and 
                    (not (building_not_built ?t ?l))
                    (building_built ?t ?l)
                )
            )
        )
    )
)