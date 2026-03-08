(import-rdf "facts.rdf")

(export-rdf export.rdf  guilty_258_basic guilty_258_qualified guilty_260_basic guilty_260_gain guilty_260_high guilty_260_very_high has_mitigating has_aggravating mitigation_allowed suspended_sentence_possible to_imprison_min to_imprison_max)

(export-proof proof.ruleml)

(defeasiblerule rule1
	(declare (superior rule3 ))
	(lc:case (lc:defendant ?Defendant) (lc:article "258")) 
  => 
	(guilty_258_basic (defendant ?Defendant)) 
) 

(defeasiblerule rule2
	(lc:case (lc:defendant ?Defendant) (lc:article "258")) 
	(lc:case (lc:defendant ?Defendant) (lc:amount_over_15000 "yes")) 
  => 
	(guilty_258_qualified (defendant ?Defendant)) 
) 

(defeasiblerule rule3
	(lc:case (lc:defendant ?Defendant) (lc:article "258")) 
	(lc:case (lc:defendant ?Defendant) (lc:amount_over_15000 "yes")) 
  => 
	(not 
	(guilty_258_basic (defendant ?Defendant)) 
	)
) 

(defeasiblerule rule4
	(declare (superior rule6 ))
	(lc:case (lc:defendant ?Defendant) (lc:article "260")) 
  => 
	(guilty_260_basic (defendant ?Defendant)) 
) 

(defeasiblerule rule5
	(declare (superior rule8 ))
	(lc:case (lc:defendant ?Defendant) (lc:article "260")) 
	(lc:case (lc:defendant ?Defendant) (lc:gained_profit "yes")) 
  => 
	(guilty_260_gain (defendant ?Defendant)) 
) 

(defeasiblerule rule6
	(lc:case (lc:defendant ?Defendant) (lc:article "260")) 
	(lc:case (lc:defendant ?Defendant) (lc:gained_profit "yes")) 
  => 
	(not 
	(guilty_260_basic (defendant ?Defendant)) 
	)
) 

(defeasiblerule rule7
	(declare (superior rule10 ))
	(lc:case (lc:defendant ?Defendant) (lc:article "260")) 
	(lc:case (lc:defendant ?Defendant) (lc:amount_over_3000 "yes")) 
  => 
	(guilty_260_high (defendant ?Defendant)) 
) 

(defeasiblerule rule8
	(lc:case (lc:defendant ?Defendant) (lc:article "260")) 
	(lc:case (lc:defendant ?Defendant) (lc:amount_over_3000 "yes")) 
  => 
	(not 
	(guilty_260_gain (defendant ?Defendant)) 
	)
) 

(defeasiblerule rule9
	(lc:case (lc:defendant ?Defendant) (lc:article "260")) 
	(lc:case (lc:defendant ?Defendant) (lc:amount_over_30000 "yes")) 
  => 
	(guilty_260_very_high (defendant ?Defendant)) 
) 

(defeasiblerule rule10
	(lc:case (lc:defendant ?Defendant) (lc:article "260")) 
	(lc:case (lc:defendant ?Defendant) (lc:amount_over_30000 "yes")) 
  => 
	(not 
	(guilty_260_high (defendant ?Defendant)) 
	)
) 

(defeasiblerule rule11
	(lc:case (lc:defendant ?Defendant) (lc:confession "yes")) 
  => 
	(has_mitigating (defendant ?Defendant)) 
) 

(defeasiblerule rule12
	(lc:case (lc:defendant ?Defendant) (lc:prior_conviction "no")) 
  => 
	(has_mitigating (defendant ?Defendant)) 
) 

(defeasiblerule rule13
	(lc:case (lc:defendant ?Defendant) (lc:restitution "yes")) 
  => 
	(has_mitigating (defendant ?Defendant)) 
) 

(defeasiblerule rule14
	(lc:case (lc:defendant ?Defendant) (lc:remorse "yes")) 
  => 
	(has_mitigating (defendant ?Defendant)) 
) 

(defeasiblerule rule15
	(lc:case (lc:defendant ?Defendant) (lc:has_children "yes")) 
  => 
	(has_mitigating (defendant ?Defendant)) 
) 

(defeasiblerule rule16
	(lc:case (lc:defendant ?Defendant) (lc:cooperation "yes")) 
  => 
	(has_mitigating (defendant ?Defendant)) 
) 

(defeasiblerule rule17
	(lc:case (lc:defendant ?Defendant) (lc:prior_conviction "yes")) 
  => 
	(has_aggravating (defendant ?Defendant)) 
) 

(defeasiblerule rule18
	(lc:case (lc:defendant ?Defendant) (lc:organized_crime "yes")) 
  => 
	(has_aggravating (defendant ?Defendant)) 
) 

(defeasiblerule rule19
	(declare (superior rule20 ))
	(has_mitigating (defendant ?Defendant)) 
  => 
	(mitigation_allowed (defendant ?Defendant)) 
) 

(defeasiblerule rule20
	(has_aggravating (defendant ?Defendant)) 
  => 
	(not 
	(mitigation_allowed (defendant ?Defendant)) 
	)
) 

(defeasiblerule rule21
	(declare (superior rule22 ))
	(has_mitigating (defendant ?Defendant)) 
  => 
	(suspended_sentence_possible (defendant ?Defendant)) 
) 

(defeasiblerule rule22
	(has_aggravating (defendant ?Defendant)) 
  => 
	(not 
	(suspended_sentence_possible (defendant ?Defendant)) 
	)
) 

(defeasiblerule pen1
	(guilty_258_basic (defendant ?Defendant)) 
  => 
	(to_imprison_min (value 24)) 
) 

(defeasiblerule pen2
	(guilty_258_basic (defendant ?Defendant)) 
  => 
	(to_imprison_max (value 144)) 
) 

(defeasiblerule pen3
	(guilty_258_qualified (defendant ?Defendant)) 
  => 
	(to_imprison_min (value 60)) 
) 

(defeasiblerule pen4
	(guilty_258_qualified (defendant ?Defendant)) 
  => 
	(to_imprison_max (value 180)) 
) 

(defeasiblerule pen5
	(guilty_260_basic (defendant ?Defendant)) 
  => 
	(to_imprison_max (value 36)) 
) 

(defeasiblerule pen6
	(guilty_260_gain (defendant ?Defendant)) 
  => 
	(to_imprison_min (value 6)) 
) 

(defeasiblerule pen7
	(guilty_260_gain (defendant ?Defendant)) 
  => 
	(to_imprison_max (value 60)) 
) 

(defeasiblerule pen8
	(guilty_260_high (defendant ?Defendant)) 
  => 
	(to_imprison_min (value 12)) 
) 

(defeasiblerule pen9
	(guilty_260_high (defendant ?Defendant)) 
  => 
	(to_imprison_max (value 96)) 
) 

(defeasiblerule pen10
	(guilty_260_very_high (defendant ?Defendant)) 
  => 
	(to_imprison_min (value 24)) 
) 

(defeasiblerule pen11
	(guilty_260_very_high (defendant ?Defendant)) 
  => 
	(to_imprison_max (value 120)) 
) 
