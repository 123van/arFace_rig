def ctrlConnectBlendShape():    

    #curve blendShape connection
    if cmds.objExists("*LipCrvBS") & cmds.objExists("*browBS") & cmds.objExists("*CheekBS"):
        typeCList ={ "mouth_happysad":[["upHappy_crv", "loHappy_crv", "happyCheek_crv" ],["upSad_crv", "loSad_crv", "sadCheek_crv"]] }

        for LR in ["l_","r_"]:
            # "B"type ctl setup
            if not cmds.listConnections( LR+ "brow_Furrow", s=0, d=1 ):
                BCDtypeCtrlSetup.BCtrlSetup( LR + "brow_Furrow", LR, "y", LR[0]+ "Furrow_crv" , LR[0]+ "Relax_crv" )
            else:
                print "%s already have connections"%(LR+ "brow_Furrow")
            
            if not cmds.listConnections( LR+ "brow_madsad", s=0, d=1 ):
                BCDtypeCtrlSetup.CCtrlSetup( LR + "brow_madsad", LR, ["y","x"], [ LR[0]+ "BrowSad_crv" ], [  LR[0]+ "BrowMad_crv" ] )     
            else:
                print "%s already have connections"%(LR+ "brow_madsad" )       
            
            # "C"type ctl setup
            for C, cList in typeCList.iteritems():
            	if not cmds.listConnections( LR+ C, s=0, d=1 ):#if there is no connections to the ctl
            	    cListA = [ LR+ x for x in cList[0] ]
            	    cListB = [ LR+ x for x in cList[1] ]
            	    CCtrlSetup( LR+C, LR, ["y","x"], cListA, cListB )
                else:
                    print "%s already have connections"%( LR+C )
                    
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
            else:
                print "%s already have connections"%( LR + "phonemes_ctl" )
                                
    #mesh blendShape connection          
    if cmds.objExists("twitchBS"):

        typeAList ={ "sneer":"nose_sneer.ty", "flare":"nose_flare.ty", "squint": "squint_remap.outValue", "annoy":"annoy_remap.outValue" }
        typeBList ={ "brow_Furrow":["furrow", "relax"], "bridge_puffsuck":["puff", "suck"], "ShM":["Sh", "M"] }
        typeCList ={ "mouth_happysad":["happy", "sad"], "brow_madsad": ["browSad", "browMad"] }
        
        for LR in ["l_","r_"]:
            for A, attr in typeAList.iteritems():
                if not cmds.listConnections( "twitchBS." + LR+ A, s=1, d=0 ):
                    cmds.connectAttr( LR + attr, "twitchBS." + LR + A )
                else:
                    print "twitchBS.%s already has connections"%( LR+ A)    
         
            for B in typeBList:
                if not cmds.listConnections( LR+ B, s=0, d=1 ):
                    print LR + B
                    BCDtypeCtrlSetup.BCtrlSetup( LR + B, LR, "y", LR+ typeBList[B][0], LR+ typeBList[B][1] )  
                else:
                    print LR+"shit"
                    clamp = cmds.listConnections( LR+ B, s=0, d=1, type = "clamp")
                    cmds.connectAttr( clamp[0]+ ".outputR", "twitchBS." + LR+ typeBList[B][0] )
                    cmds.connectAttr( clamp[0] + ".outputG", "twitchBS." + LR+ typeBList[B][1] )
                    
            for C in typeCList:
                if not cmds.listConnections( LR+ C, s=0, d=1 ):
                    BCDtypeCtrlSetup.CCtrlSetup( LR+ C, LR, ["y","x"], [ LR+typeCList[C][0] ], [ LR+typeCList[C][1] ] )
                else:
                    remap = cmds.listConnections( LR+ C, s=0, d=1, type = "remapValue")
                    cmds.connectAttr( remap[0]+ ".outValue", "twitchBS." + LR+typeCList[C][0] )
                    cmds.connectAttr( remap[0].replace("pos", "neg") + ".outValue", "twitchBS." + LR+typeCList[C][1] )      
    
            # phoneme "D" type ctrl setup 
            if cmds.listConnections( LR+ "phonemes_ctl", s=0, d=1 ):
                if not cmds.listConnections( "twitchBS." + LR+ "U", s=1, d=0 ):
                    cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "twitchBS." + LR+ "U" ) 
                
                if not cmds.listConnections( "twitchBS." + LR+ "E", s=1, d=0 ):
                    cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", "twitchBS." + LR+ "E" )                         

                if not cmds.listConnections( "twitchBS." + LR+ "O", s=1, d=0 ):
                    cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", "twitchBS." + LR+ "O" )                     

                if not cmds.listConnections( "twitchBS." + LR+ "wide", s=1, d=0 ):
                    cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", "twitchBS." + LR+ "wide" ) 
            else:
                BCDtypeCtrlSetup.DCtrlSetup( LR + "phonemes_ctl", LR+"phoneme", "lip")
                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "twitchBS." + LR+ "U" )                

                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", "twitchBS." + LR+ "E" )                

                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", "twitchBS." + LR+ "O" )                

                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", "twitchBS." + LR+ "wide" )  
