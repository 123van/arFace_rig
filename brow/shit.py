def ctrlConnectBlendShape():

	#curve blendShape connection
    if cmds.objExists("*LipCrvBS") & cmds.objExists("*browBS") & cmds.objExists("*CheekBS"):
        typeCList ={ "mouth_happysad":[["upHappy_crv", "loHappy_crv", "happyCheek_crv" ],["upSad_crv", "loSad_crv", "sadCheek_crv"]] }

        for LR in ["l_","r_"]:
            # "B"type ctl setup
            if not cmds.listConnections( LR+ "brow_Furrow", s=0, d=1 ):
                BCDtypeCtrlSetup.BCtrlSetup( LR + "brow_Furrow", LR, "y", [ LR[0]+ "Furrow_crv" ], [  LR[0]+ "Relax_crv" ] )     
            
            if not cmds.listConnections( LR+ "brow_madsad", s=0, d=1 ):
                BCDtypeCtrlSetup.CCtrlSetup( LR + "brow_madsad", LR, ["y","x"], [ LR[0]+ "BrowSad_crv" ], [  LR[0]+ "BrowMad_crv" ] )     
            # "C"type ctl setup
            for C, cList in typeCList.iteritems():
            	if not cmds.listConnections( LR+ C, s=0, d=1 ):#if there is no connections to the ctl
            	    cListA = [ LR+ x for x in cList[0] ]
            	    cListB = [ LR+ x for x in cList[1] ]
            	    BCDtypeCtrlSetup.CCtrlSetup( LR+C, LR, ["y","x"], cListA, cListB )

            # phoneme "D" type ctrl setup
            if not cmds.listConnections( LR+ "phonemes_ctl", s=0, d=1 ):
                BCDtypeCtrlSetup.DCtrlSetup( LR + "phonemes_ctl", LR+"phoneme", "lip")   
         
                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "upLipCrvBS." + LR+ "upU_crv" )
                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "loLipCrvBS." + LR+ "loU_crv" )
                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", LR[0] + "CheekBS." + LR+ "uCheek_crv" )
                       
                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", "upLipCrvBS." + LR+ "uplipE_crv" )
                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", "loLipCrvBS." + LR+ "lolipE_crv" )
                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", LR[0] + "CheekBS." + LR+ "eCheek_crv" )
                
                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", "upLipCrvBS." + LR+ "upO_crv" )
                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", "loLipCrvBS." + LR+ "loO_crv" )
                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", LR[0] + "CheekBS." + LR+ "oCheek_crv" )
                
                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", "upLipCrvBS." + LR+ "uplipWide_crv" )
                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", "loLipCrvBS." + LR+ "lolipWide_crv" )
                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", LR[0] + "CheekBS." + LR+ "wideCheek_crv" )    

    if cmds.objExists("twitchBS"):
        typeAList ={ "sneer":"nose_sneer.ty", "flare":"nose_flare.ty", "squint": "squint_remap.outValue", "annoy":"annoy_remap.outValue" }
        typeBList ={ "brow_Furrow":["furrow", "relax"], "bridge_puffsuck":["puff", "suck"], "ShM":["Sh", "M"] }
        typeCList ={ "mouth_happysad":["happy", "sad"], "brow_madsad": ["browSad", "browMad"] }
        alias = cmds.aliasAttr( "twitchBS", q=1 )
        for LR in ["l_","r_"]:
            '''for A, attr in typeAList.iteritems():
                if not cmds.listConnections( "twitchBS." + LR+ A, s=1, d=0 ):
                    cmds.connectAttr( LR + attr, "twitchBS." + LR + A )
                    print A'''
            for B, trgt in typeBList.iteritems():
                if not cmds.listConnections( LR+ B, s=0, d=1 ):
                    BCDtypeCtrlSetup.BCtrlSetup( LR + B, "y", LR+ trgt[0], LR+ trgt[1] )  
                    print B, trgt
            for C, tgt in typeCList.iteritems():
                if not cmds.listConnections( LR+ C, s=0, d=1 ):
                    BCDtypeCtrlSetup.CCtrlSetup( LR+ C, LR, ["y","x"], [ LR+tgt[0] ], [ LR+tgt[1] ] )      
                    print C
            # phoneme "D" type ctrl setup 
            if not cmds.listConnections( LR+ "phonemes_ctl", s=0, d=1 ):
                BCDtypeCtrlSetup.DCtrlSetup( LR + "phonemes_ctl", LR+"phoneme", "lip")
                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "twitchBS." + LR+ "U" )                

                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", "twitchBS." + LR+ "E" )                

                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", "twitchBS." + LR+ "O" )                

                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", "twitchBS." + LR+ "wide" )     