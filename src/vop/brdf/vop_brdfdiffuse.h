//
// Copyright (c) 2015, Chaos Software Ltd
//
// V-Ray For Houdini
//
// Andrei Izrantcev <andrei.izrantcev@chaosgroup.com>
//
// All rights reserved. These coded instructions, statements and
// computer programs contain unpublished information proprietary to
// Chaos Software Ltd, which is protected by the appropriate copyright
// laws and may not be disclosed to third parties or copied or
// duplicated, in whole or in part, without prior written consent of
// Chaos Software Ltd.
//

#ifndef VRAY_FOR_HOUDINI_VOP_NODE_BRDFDIFFUSE_H
#define VRAY_FOR_HOUDINI_VOP_NODE_BRDFDIFFUSE_H

#include "vop_node_base.h"


namespace VRayForHoudini {
namespace VOP {


class BRDFDiffuse:
		public NodeBase
{
public:
	BRDFDiffuse(OP_Network *parent, const char *name, OP_Operator *entry):NodeBase(parent, name, entry) {}
	virtual                  ~BRDFDiffuse() {}

	virtual void              getCode(UT_String &codestr, const VOP_CodeGenContext &context) VRAY_OVERRIDE;

protected:
	virtual void              setPluginType() VRAY_OVERRIDE;

}; // BRDFDiffuse

} // namespace VOP
} // namespace VRayForHoudini

#endif // VRAY_FOR_HOUDINI_VOP_NODE_BRDFDIFFUSE_H